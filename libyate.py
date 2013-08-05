#!/usr/bin/env python
import datetime
import select
import sys

KW_CONNECT = '%%>connect'
KW_ERROR = 'Error in'
KW_INSTALL = '%%>install'
KW_INSTALLREPLY = '%%<install'
KW_MESSAGE = '%%>message'
KW_MESSAGEREPLY = '%%<message'
KW_OUTPUT = '%%>output'
KW_SETLOCAL = '%%>setlocal'
KW_SETLOCALREPLY = '%%<setlocal'
KW_UNINSTALL = '%%>uninstall'
KW_UNINSTALLREPLY = '%%<uninstall'
KW_UNWATCH = '%%>unwatch'
KW_UNWATCHREPLY = '%%<unwatch'
KW_WATCH = '%%>watch'
KW_WATCHREPLY = '%%<watch'

KW_MAP = {
    '%%>message': ['method', 'id', 'timestamp', 'name', 'retval', 'extras'],
    '%%<message': ['method', 'id', 'processed', 'name', 'retval', 'extras'],
    '%%>install': ['method', 'priority', 'name', 'filtername', 'filtervalue'],
    '%%<install': ['method', 'priority', 'name', 'success'],
    '%%>uninstall': ['method', 'name'],
    '%%<uninstall': ['method', 'priority', 'name', 'success'],
    'Error in': ['command'],
}


class Poller:
    def __init__(self, fd):
        self.fd = fd

        if hasattr(select, 'epoll'):
            self.poller = select.epoll()
            self.poller.register(self.fd, select.EPOLLIN)
        elif hasattr(select, 'poll'):
            self.poller = select.poll()
            self.poller.register(self.fd, select.POLLIN)

    def __del__(self):
        if hasattr(select, 'epoll') or hasattr(select, 'poll'):
            self.poller.unregister(self.fd)

    def poll(self):
        if hasattr(select, 'epoll') or hasattr(select, 'poll'):
            self.poller.poll()
        else:
            select.select([self.fd], [], [])
        return self.fd.readline()


def cmd_to_dict(command):
    '''Read a command line and parse into a dict'''

    # Remove line-feed
    command = command.rstrip('\n')

    # Get the method name
    method = command.split(':', 1)[0]

    # Get the keys names for this method
    try:
        keys = KW_MAP[method]
    except KeyError:
        raise NotImplementedError('Method "{}" not implemented'.format(method))

    # Map the keys to the values
    command = dict(zip(keys, command.split(':', len(keys)-1)))

    # Decode the values
    for key in command.keys():
        if key == 'extras':
            # Map the key-value pairs into a dict
            for x, y in [z.split('=') for z in command[key].split(':')]:
                command[str_decode(x)] = str_decode(y)
            del command[key]
        elif key == 'priority':
            command[key] = int(command[key])
        elif key == 'processed':
            command[key] = True if command[key] == 'true' else False
            print command[key]
        elif key == 'success':
            command[key] = True if command[key] == 'true' else False
        elif key == 'timestamp':
            command[key] = datetime.datetime.fromtimestamp(int(command[key]))
        elif key == 'method':
            pass
        else:
            command[key] = str_decode(command[key])

    return command


def dict_to_cmd(command):
    '''Parse a dict into a command line'''

    # Get the keys names for this method
    try:
        keys = KW_MAP[command['method']]
    except KeyError:
        raise NotImplementedError('Method "{}" not implemented'
                                  .format(command['method']))

    reply = [command.pop('method', '')]

    # Default attributes
    for key in keys:
        if key == 'timestamp':
            reply.append(command.pop(key, datetime.datetime.now())
                         .strftime('%s'))
        elif key == 'priority':
            reply.append(str(command.pop(key, '')))
        elif key == 'processed':
            reply.append('true' if command.pop(key, False) else 'false')
        elif key == 'success':
            reply.append('true' if command.pop(key, False) else 'false')
        elif key == 'extras':
            pass
        elif key == 'method':
            pass
        else:
            reply.append(str_encode(command.pop(key, '')))

    # Extra attributes
    for key, value in command.items():
        reply.append('='.join((str_encode(key), str_encode(value))))

    return ':'.join(reply) + '\n'


def lower(char):
    '''Get the original form form a upcoded char'''
    if char == '%':
        return '%'
    else:
        return chr(ord(char)-64)


def str_decode(string):
    '''Return a escaped string to the original from'''
    if '%' in string:
        string, encoded = string.split('%', 1)

        string += lower(encoded[0])

        if len(encoded) > 1:
            string += str_decode(encoded[1:])

    return string


def str_encode(string):
    '''Escape a string upcoding the characters'''
    return ''.join(upper(char) for char in list(string))


def upper(char):
    '''Upcode a char'''
    if ord(char) < 32 or char == ':':
        return '%' + chr(64+ord(char))
    elif char == '%':
        return '%%'
    else:
        return char


def run():
    sys.stderr.write('Loading test script: {}\n'.format(__file__))
    stdin = Poller(sys.stdin)

    while True:
        line = stdin.poll()

        if line:
            sys.stderr.write('Received: {}\n'.format(line.strip()))
            try:
                cmd = cmd_to_dict(line)
            except Exception, e:
                sys.stderr.write(e.message + '\n')
            else:
                if cmd['method'] == KW_MESSAGE:
                    reply = cmd.copy()
                    del reply['timestamp']
                    reply.update({
                        'method': KW_MESSAGEREPLY,
                        'testing': 'true',
                    })

                    sys.stderr.write('Reply: {}'.format(dict_to_cmd(reply)))


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        pass
