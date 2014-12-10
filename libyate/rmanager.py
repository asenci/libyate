"""
libyate - remote manager client
"""

import logging
import re
import socket
import telnetlib


class RManagerException(Exception):
    """Base exception for RManagerSession"""
    pass


class AuthenticationException(RManagerException):
    """Authentication errors"""
    pass


class PermissionException(RManagerException):
    """Authorization errors"""
    pass


class RuntimeException(RManagerException):
    """Execution errors"""
    pass


class SyntaxException(RManagerException):
    """Syntax errors"""
    pass


class RManagerSession(object):
    """Yate rmanager client"""

    def __init__(self, host='127.0.0.1', port=5038, password=None):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.__input_buffer__ = ''
        self._socket = None
        self._auth_level = None

        self.connect(host, port)

        # Get greeting message
        self.header = self.readline()

        # Disable local output (authenticated as 'user' if successful)
        self.write('output off\r\n')
        for line in self:
            if line == 'Output mode: off':
                self._auth_level = 'user'
                break

            elif line == 'Not authenticated!':
                break

        if self._auth_level is None and password is None:
            raise AuthenticationException('Server requires authentication')

        # Disable debugging output (authenticated as 'admin' if successful)
        self.write('debug off\r\n')
        for line in self:
            if line.startswith('Debug level: '):
                self._auth_level = 'admin'
                break

            elif line == 'Not authenticated!':
                break

        # Try authenticating with the provided password
        if password:
            self.auth(password)

        # Disable output coloring
        self.color(False)

    def __del__(self):
        self.close()

    def __iter__(self):
        while True:
            yield self.readline()

    def connect(self, host, port):
        """Open a socket connection to the provided host and port

        :param str host: host address
        :param int port: host port
        """

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
        """Receive data from the host and process Telnet commands

        :return: A line of data
        :rtype: str
        """

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
        """Send data to the host

        :param str string: Data to send to the host
        :raise IOError: on input/output errors
        """

        if self._socket is None:
            raise IOError('Socket closed')

        self.logger.debug('Sending {0} bytes: {1!r}'
                          .format(len(string), string))

        try:
            self._socket.sendall(string)

        except socket.error as e:
            raise IOError(str(e))

    def close(self):
        """Disconnect from the host and cleanup"""

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
        """Send commands to the host and get the reply

        :param str command: Command to send to the host
        :return: The command reply
        :rtype: str
        """

        # Send the command through the socket
        self.write('{0}\r\n'.format(command))

        # Read reply
        for line in self:

            # Invalid command
            if line.startswith('Cannot understand: '):
                raise SyntaxException(line)

            # Not authorized to execute the command
            elif line == 'Not authenticated!':
                raise PermissionException(line)

            # Multi-line replies (eg: status command)
            elif line.startswith('%%+'):
                result = []

                for next_line in self:

                    if next_line.startswith('%%-'):
                        return '\r\n'.join(result)

                    result.append(next_line)

            return line

    def auth(self, password=None):
        """Show the authentication level or authenticate so you can access
        privileged commands if a password is provided

        :param str password: The authentication password
        :return: The current authentication level
        :rtype: str
        :raise AuthenticationException: if the provided password is not valid
        """

        if password:
            result = self.send_cmd('auth {0}'.format(password))

            if result in ['Authenticated successfully as admin!',
                          'You are already authenticated as admin!']:
                self._auth_level = 'admin'

            elif result in ['Authenticated successfully as user!',
                            'You are already authenticated as user!']:
                self._auth_level = 'user'

            else:
                raise AuthenticationException(result)

        return self._auth_level

    def call(self, channel, target):
        """Execute an outgoing call

        :param str channel: The channel that will be connected
        :param str target: The call target
        :return: The command result
        :rtype: str
        :raise RuntimeException: if the call can not be processed
        """
        result = self.send_cmd('call {0} {1}'.format(channel, target))

        if result.startswith('Calling '):
            return result

        raise RuntimeException(result)

    def color(self, enable=True):
        """Turn local colorization on or off

        :param bool enable: Enable output coloring if True, disable if False
        :return: The command result
        :rtype: str
        """

        return self.send_cmd('color {0}'.format('on' if enable else 'off'))

    def control(self, channel, operation, **kwargs):
        """Apply arbitrary control operations to a channel or entity

        :param str channel: Which channel or entity to control
        :param str operation: The operation to be executed
        :param dict kwargs: Additional parameters to the operation
        :return: The command result
        :rtype: str
        :raise RuntimeException: if the operation can not be executed
        """
        args = ' '.join(('='.join((k, v)) for k, v in kwargs.items()))

        result = self.send_cmd('control {0} {1} {2}'.format(
            channel, operation, args))

        if result.endswith('OK'):
            return result

        raise RuntimeException(result)

    def drop(self, channel, reason=''):
        """Drops one or all active calls

        :param str channel: Which channel to drop
        :param str reason: The hangup reason
        :return: The command result
        :rtype: str
        :raise RuntimeException: if the call can not be dropped
        """
        result = self.send_cmd('drop {0} {1}'.format(channel, reason))

        if result.startswith('Dropped ') or \
                result.startswith('Tried to drop '):
            return result

        raise RuntimeException(result)

    def reload(self, plugin=''):
        """Reloads module configuration files

        :param str plugin: Which plugin to reload
        :return: The command result
        :rtype: str
        :raise RuntimeException: if the plugin configuration can not be
        reloaded
        """
        result = self.send_cmd('reload {0}'.format(plugin))

        if result == 'Reinitializing...':
            return result

        raise RuntimeException(result)

    def restart(self, graceful=True):
        """Restarts the engine if executing supervised

        :param bool graceful: Execute a graceful restart if True, restart
        immediately if False
        :return: The command result
        :rtype: str
        :raise RuntimeException: if the engine can not be restarted
        """
        result = self.send_cmd('restart {0}'.format(
            'now' if not graceful else ''))

        if result == 'Restart scheduled - please disconnect' or \
                result == 'Engine restarting - bye!':
            return result

        raise RuntimeException(result)

    def status(self, module='', overview=False):
        """Shows status of all or selected modules or channels

        :param str module: Which module status will be retrieved
        :param bool overview: Get only the status overview if True, get the
        details if False
        :return: A dictionary containing the modules status
        :rtype: dict
        """
        status_list = self.send_cmd('status {0} {1}'.format(
            'overview' if overview else '', module))

        result = []

        for line in status_list.splitlines():
            # Definition, status and details groups are separated by ';'
            definition, status = line.partition(';')[::2]
            status, details = status.partition(';')[::2]

            # Attributes are represented by key=value pairs separated by ','
            definition = dict((x.partition('=')[::2])
                              for x in definition.split(','))

            if status:
                status = dict((x.partition('=')[::2])
                              for x in status.split(','))

            if details:
                details = dict((x.partition('=')[::2])
                               for x in details.split(','))

                # Nodes attributes are separated by '|'
                # Attributes names are optionally defined on the 'format'
                # attribute
                if definition.get('format') is not None:
                    fmt = definition.get('format').split('|')
                    for k, v in details.items():
                        details[k] = dict(zip(fmt, v.split('|')))

            result.append({
                'definition': definition,
                'status': status or {},
                'details': details or {},
            })

        return result

    def stop(self, exitcode=''):
        """Stops the engine with optionally provided exit code

        :param str exitcode: The exit code to return
        :return: The command result
        :rtype: str
        :raise RuntimeException: if the engine can not be stopped
        """
        result = self.send_cmd('stop {0}'.format(exitcode))

        if result == 'Engine shutting down - bye!':
            return result

        raise RuntimeException(result)

    def uptime(self, name=None):
        """Show information on how long Yate has run

        :param str name: Which uptime will be retrieved
        :return: How many seconds Yate has run for
        :rtype: float
        """
        result = self.send_cmd('uptime')

        m = re.match(r'^Uptime: \d+ \d{2}:\d{2}:\d{2} \((?P<total>\d+)\)'
                     r' user: (?P<user>\d+.\d{3})'
                     r' kernel: (?P<kernel>\d+.\d{3})$', result)

        if name is None:
            return dict((k, float(v)) for k, v in m.groupdict().items())

        try:
            return float(m.groupdict()[name])
        except KeyError:
            raise SyntaxException('{0} uptime not supported'.format(name))
