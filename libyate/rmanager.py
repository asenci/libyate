"""
libyate - remote manager client
"""

import logging
import re
import socket
import telnetlib


class RManagerException(Exception):
    pass


class AuthenticationException(RManagerException):
    pass


class PermissionException(RManagerException):
    pass


class SyntaxException(RManagerException):
    pass


class RManagerSession(object):

    def __init__(self, host='127.0.0.1', port=5038, auth=None):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.__input_buffer__ = ''
        self._socket = None
        self.auth_level = None

        self.connect(host, port)

        self.header = self.readline()

        self.write('echo off\r\n')
        for line in self:
            if line == 'Remote echo: off':
                break

        self.write('output off\r\n')
        for line in self:
            if line == 'Output mode: off':
                self.auth_level = 'user'
                break

            elif line == 'Not authenticated!':
                break

        if self.auth_level is not None:
            self.write('color off\r\n')
            for line in self:
                if line == 'Colorized output: no':
                    break

        self.write('debug off\r\n')
        for line in self:
            if line.startswith('Debug level: '):
                self.auth_level = 'admin'
                break

            elif line == 'Not authenticated!':
                break

        if auth is not None:
            self.auth(auth)

        elif self.auth_level is None:
            raise AuthenticationException('Server requires authentication')

    def __del__(self):
        self.close()

    def __iter__(self):
        while True:
            yield self.readline()

    def connect(self, host, port):
        if self._socket is not None:
            self._socket.close()

        # Get protocols and addresses
        l = socket.getaddrinfo(
            host, port,
            socket.AF_UNSPEC, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        while l:

            # Get connection data
            f, t, p, c, a = l.pop()

            # Try to create the socket
            try:
                self._socket = socket.socket(f, t, p)

            # Error creating the socket
            except socket.error:

                # Try next resource
                if l:
                    continue

                # No resources left
                raise

            # Try to connect to the address
            try:
                self._socket.connect(a)

            # Error connecting to the address
            except socket.error:
                self._socket.close()

                # Try next resource
                if l:
                    continue

                # No resources left
                raise

            # Socket connected, continue execution
            break

    def readline(self):
        # Continue receiving until '\r\n' is received
        while '\r\n' not in self.__input_buffer__:

            if self._socket is None:
                data = ''

            else:
                try:
                    data = self._socket.recv(8192)
                except socket.error as e:
                    raise IOError(str(e))

            if data == '':
                raise EOFError('Socket closed')

            self.logger.debug('Received {0} bytes: {1!r}'
                              .format(len(data), data))

            # Telnet commands
            while telnetlib.IAC in data:
                iac_pos = data.find(telnetlib.IAC)
                cmd = data[iac_pos + 1]

                # Option negotiation
                if cmd in [telnetlib.DO, telnetlib.DONT,
                           telnetlib.WILL, telnetlib.WONT]:

                    opt = data[iac_pos + 2]
                    data = data[:iac_pos] + data[iac_pos+3:]

                    if cmd == telnetlib.DO:
                        self.write(telnetlib.IAC + telnetlib.WONT + opt)
                    elif cmd == telnetlib.WILL:
                        self.write(telnetlib.IAC + telnetlib.DONT + opt)

            self.__input_buffer__ += data

        line, self.__input_buffer__ = \
            self.__input_buffer__.partition('\r\n')[::2]

        return line

    def write(self, string):
        if self._socket is None:
            raise IOError('Socket closed')

        self.logger.debug('Sending {0} bytes: {1!r}'
                          .format(len(string), string))

        try:
            self._socket.sendall(string)

        except socket.error as e:
            raise IOError(str(e))

    def close(self):
        if self._socket is not None:
            try:
                reply = self.send_cmd('quit')

                if reply != 'Goodbye!':
                    self.logger.error(reply)

            except (IOError, EOFError):
                pass

            self._socket.close()
            self._socket = None

        self.__input_buffer__ = ''

    def send_cmd(self, command):
        self.write('{0}\r\n'.format(command))

        for line in self:

            if line.startswith('Cannot understand: '):
                raise SyntaxException(line)

            elif line == 'Not authenticated!':
                raise PermissionException(line)

            elif line.startswith('%%+'):
                result = []

                for next_line in self:

                    if next_line.startswith('%%-'):
                        return result

                    result.append(next_line)

            return line

    def auth(self, password):
        result = self.send_cmd('auth {0}'.format(password))

        if result == 'Bad authentication password!':
            raise AuthenticationException(result)

        elif result in ['Authenticated successfully as admin!',
                        'You are already authenticated as admin!']:
            self.auth_level = 'admin'

        else:
            self.auth_level = 'user'

    def uptime(self, usage=None):
        result = self.send_cmd('uptime')

        m = re.match(r'^Uptime: \d+ \d{2}:\d{2}:\d{2} \((?P<total>\d+)\)'
                     r' user: (?P<user>\d+.\d{3})'
                     r' kernel: (?P<kernel>\d+.\d{3})$', result)

        if usage is None:
            return dict((k, float(v)) for k, v in m.groupdict().items())

        try:
            return float(m.groupdict()[usage])
        except KeyError:
            raise KeyError('{0} usage not supported'.format(usage))

    def status(self, module=None):
        if module is not None:
            status_list = self.send_cmd('status {0}'.format(module))
        else:
            status_list = self.send_cmd('status')

        result = []

        for line in status_list:
            # Definition, status and nodes groups are separated by ';'
            definition, status = line.partition(';')[::2]
            status, nodes = status.partition(';')[::2]

            # Attributes are represented by key=value pairs separated by ','
            definition = dict((x.partition('=')[::2])
                              for x in definition.split(','))
            status = dict((x.partition('=')[::2])
                          for x in status.split(','))
            nodes = dict((x.partition('=')[::2])
                         for x in nodes.split(','))

            # Nodes attributes are separated by '|'
            # Attributes names are optionally defined on the 'format' attribute
            if definition.get('format') is not None:
                fmt = definition.get('format').split('|')
                for k, v in nodes.items():
                    nodes[k] = dict(zip(fmt, v.split('|')))

            result.append({
                'definition': definition,
                'status': status,
                'nodes': nodes,
            })

        return result
