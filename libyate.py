#!/usr/bin/env python
import datetime
import logging
import random


# Keywords definition
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
    KW_CONNECT: ['method', 'role', 'id', 'type'],
    KW_ERROR: ['method', 'command'],
    KW_INSTALL: ['method', 'priority', 'name', 'filtername', 'filtervalue'],
    KW_INSTALLREPLY: ['method', 'priority', 'name', 'success'],
    KW_MESSAGE: ['method', 'id', 'timestamp', 'name', 'retval', 'extras'],
    KW_MESSAGEREPLY: ['method', 'id', 'processed', 'name', 'retval', 'extras'],
    KW_OUTPUT: ['method', 'output'],
    KW_SETLOCAL: ['method', 'name', 'value'],
    KW_SETLOCALREPLY: ['method', 'name', 'value', 'success'],
    KW_UNINSTALL: ['method', 'name'],
    KW_UNINSTALLREPLY: ['method', 'priority', 'name', 'success'],
    KW_UNWATCH: ['method', 'name'],
    KW_UNWATCHREPLY: ['method', 'name', 'success'],
    KW_WATCH: ['method', 'name'],
    KW_WATCHREPLY: ['method', 'name', 'success'],
}


class YateApp(object):
    """Base class for Yate applications"""

    def __init__(self, debug=False, quiet=False, handler_map=None):
        """Initialize the class, optionally overriding the handlers map"""

        logging.basicConfig(**{
            'level': (logging.DEBUG if debug else
                      logging.WARN if quiet else
                      logging.INFO),
            'format': '%(message)s',
        })

        self.logger = logging.getLogger(__name__)

        self.queues = {
            KW_INSTALL: {},
            KW_MESSAGE: {},
            KW_SETLOCAL: {},
            KW_UNINSTALL: {},
            KW_UNWATCH: {},
            KW_WATCH: {},
        }

        self.handlers = {
            KW_ERROR: self.handle_error,
            KW_INSTALLREPLY: self.handle_install_reply,
            KW_MESSAGE: self.handle_message,
            KW_MESSAGEREPLY: self.handle_message_reply,
            KW_SETLOCALREPLY: self.handle_setlocal_reply,
            KW_UNINSTALLREPLY: self.handle_uninstall_reply,
            KW_UNWATCHREPLY: self.handle_unwatch_reply,
            KW_WATCHREPLY: self.handle_watch_reply,
        }

        if handler_map:
            self.handlers.update(handler_map)

    def gen_id(self, length=10):
        """Generate a random integer"""

        try:
            return random.SystemRandom().randint(10**(length-1), 10**length-1)
        except:
            return random.randint(10**(length-1), 10**length-1)

    def handle_command(self, line):
        """Handle incoming commands"""

        # Try parsing the command
        command = cmd_to_dict(line)

        # Dispatch the command to the handler based on the method
        try:
            handler = self.handlers[command['method']]
        except KeyError:
            raise NotImplementedError(
                'Method "{}" not implemented'.format(command['method']))
        else:
            self.logger.debug(
                'Using method "{}" to process the command'
                .format(handler.__name__))

        if handler:
            # Dispatch the command to the handler based on the method
            return handler(command)

    def handle_error(self, command):
        """Error reports handler"""

        raise SyntaxError('Invalid command: {command}'.format(**command))

    def handle_install_reply(self, command):
        """Install command reply handler"""

        # Try to find the command on the queue
        try:
            orig = self.queues[KW_INSTALL][command['name']]
        except KeyError:
            raise KeyError(
                'Invalid message handler name on reply: {name}'
                .format(**command))

        # Check the command result
        if command['success']:
            self.logger.info(
                'Message handler installed successfully for: {name}'
                .format(**command))
        else:
            self.logger.error(
                'Error installing message handler for: {name}'
                .format(**command))

        # Remove message from queue if done
        del orig

    def handle_message(self, command):
        """Simple messages processing handler"""

        # Try to find the message on the queue
        try:
            orig = self.queues[KW_MESSAGE][command['id']]
        except KeyError:
            # New message, store message in the queue
            self.queues[KW_MESSAGE][command['id']] = command
        else:
            # Message update, update the message in the queue
            orig.update(command)
            command = orig

        # Reply without processing
        reply = command.copy()
        reply['method'] = KW_MESSAGEREPLY
        reply.pop('timestamp', None)

        return dict_to_cmd(reply)

    def handle_message_reply(self, command):
        """Message command reply handler"""

        # Try to find the message on the queue
        try:
            orig = self.queues[KW_MESSAGE][command['id']]
        except KeyError:
            raise KeyError(
                'Invalid message ID on reply: {id}'
                .format(**command))

        # Check if the message processing is done
        if command['processed']:
            self.logger.info(
                'Processing completed on message "{id}"'
                .format(**command))
            # Remove message from queue if done
            del orig
        else:
            self.logger.debug(
                'Message acknowledged: "{id}"'
                .format(**command))
            # Else, update the message parameters
            orig.update(command)

    def handle_setlocal_reply(self, command):
        """Setlocal command reply handler"""

        # Try to find the command on the queue
        try:
            orig = self.queues[KW_SETLOCAL][command['name']]
        except KeyError:
            raise KeyError(
                'Invalid parameter name on reply: {name}'
                .format(**command))

        # Check the command result
        if command['success']:
            self.logger.info(
                'Parameter changed successfully: {name}={value}'
                .format(**command))
        else:
            self.logger.error(
                'Error changing parameter: {name}'
                .format(**command))

        # Remove message from queue if done
        del orig

    def handle_uninstall_reply(self, command):
        """Uninstall command reply handler"""

        # Try to find the command on the queue
        try:
            orig = self.queues[KW_UNINSTALL][command['name']]
        except KeyError:
            raise KeyError(
                'Invalid message handler name on reply: {name}'
                .format(**command))

        # Check the command result
        if command['success']:
            self.logger.info(
                'Message handler uninstalled successfully for: {name}'
                .format(**command))
        else:
            self.logger.error(
                'Error uninstalling message handler for: {name}'
                .format(**command))

        # Remove message from queue if done
        del orig

    def handle_unwatch_reply(self, command):
        """Unwatch command reply handler"""

        # Try to find the command on the queue
        try:
            orig = self.queues[KW_UNWATCH][command['name']]
        except KeyError:
            raise KeyError(
                'Invalid message watcher name on reply: {name}'
                .format(**command))

        # Check the command result
        if command['success']:
            self.logger.info(
                'Message watcher uninstalled successfully for: {name}'
                .format(**command))
        else:
            self.logger.error(
                'Error uninstalling message watcher for: {name}'
                .format(**command))

        # Remove message from queue if done
        del orig

    def handle_watch_reply(self, command):
        """Watch command reply handler"""

        # Try to find the command on the queue
        try:
            orig = self.queues[KW_WATCH][command['name']]
        except KeyError:
            raise KeyError(
                'Invalid message watcher name on reply: {name}'
                .format(**command))

        # Check the command result
        if command['success']:
            self.logger.info(
                'Message watcher installed successfully for: {name}'
                .format(**command))
        else:
            self.logger.error(
                'Error installing message watcher for: {name}'
                .format(**command))

        # Remove message from queue if done
        del orig

    def new_connect(self, role, id='', type=''):
        """Attach to the socket interface"""

        command = {
            'method': KW_CONNECT,
            'role': role,
            'id': id,
            'type': type,
        }

        if not command['id']:
            command['id'] = self.gen_id()

        return dict_to_cmd(command)

    def new_install(self, name, priority='', filtername='', filtervalue=''):
        """Requests the installation of a message handler"""

        command = {
            'method': KW_INSTALL,
            'priority': priority,
            'name': name,
        }

        if filtername:
            command['filtername'] = filtername
            if filtervalue:
                command['filtervalue'] = filtervalue

        self.queues[KW_INSTALL][name] = command
        return dict_to_cmd(command)

    def new_message(self, name, id='', timestamp='', retval='', **kwargs):
        """Send message to the Yate engine"""

        command = {
            'method': KW_MESSAGE,
            'id': id,
            'timestamp': timestamp,
            'name': name,
            'retval': retval,
        }

        command.update(kwargs)

        if not command['id']:
            command['id'] = self.gen_id()
        if not command['timestamp']:
            command['timestamp'] = datetime.datetime.now()

        self.queues[KW_MESSAGE][command['id']] = command
        return dict_to_cmd(command)

    def new_output(self, output):
        """Relay arbitrary output messages to engine's logging output"""

        command = {'method': KW_OUTPUT, 'output': output}

        return dict_to_cmd(command)

    def new_setlocal(self, name, value):
        """Requests the change of a local parameter"""

        command = {'method': KW_SETLOCAL, 'name': name, 'value': value}

        self.queues[KW_SETLOCAL][name] = command
        return dict_to_cmd(command)

    def new_uninstall(self, name):
        """Requests uninstalling a previously installed message handler"""

        command = {'method': KW_UNINSTALL, 'name': name}

        self.queues[KW_UNINSTALL][name] = command
        return dict_to_cmd(command)

    def new_unwatch(self, name):
        """Requests the installing of a message watcher"""

        command = {'method': KW_UNWATCH, 'name': name}

        self.queues[KW_UNWATCH][name] = command
        return dict_to_cmd(command)

    def new_watch(self, name):
        """Requests the installing of a message watcher"""

        command = {'method': KW_WATCH, 'name': name}

        self.queues[KW_WATCH][name] = command
        return dict_to_cmd(command)


class YateScript(YateApp):
    """Yate global external module"""

    def readline(self):
        line = raw_input()

        self.logger.debug('Received: {}'.format(line))

        return line

    def run(self, name=__file__):
        self.logger.info('Loading script "{}"'.format(name))

        while True:
            try:
                self.write(self.handle_command(self.readline()))
            except EOFError:
                self.logger.info('End of stream')
                break
            except Exception, e:
                self.logger.error(e.message)

    def write(self, line):
        if line:
            self.logger.debug('Sending: {}'.format(line))
            print(line)


class YateSocketClient(YateApp):
    """TODO: implement a class for IP/socket connecting app"""
    pass


def cmd_to_dict(command):
    """Read a command line and parse into a dict"""

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
        elif key == 'success':
            command[key] = True if command[key] == 'true' else False
        elif key == 'timestamp':
            command[key] = datetime.datetime.fromtimestamp(int(command[key]))
        elif key == 'output':
            pass
        elif key == 'method':
            pass
        else:
            command[key] = str_decode(command[key])

    return command


def dict_to_cmd(command):
    """Parse a dict into a command line"""

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
        elif key == 'output':
            reply.append(str(command.pop(key, '')))
        elif key == 'extras':
            pass
        elif key == 'method':
            pass
        else:
            reply.append(str_encode(str(command.pop(key, ''))))

    # Extra attributes
    for key, value in command.items():
        reply.append('='.join((str_encode(str(key)),
                               str_encode(str(value)))))

    return ':'.join(reply)


def lower(char):
    """Get the original form form a upcoded char"""

    if char == '%':
        return '%'
    else:
        return chr(ord(char)-64)


def str_decode(string):
    """Return a escaped string to the original from"""

    if '%' in string:
        string, encoded = string.split('%', 1)

        string += lower(encoded[0])

        if len(encoded) > 1:
            string += str_decode(encoded[1:])

    return string


def str_encode(string):
    """Escape a string upcoding the characters"""

    return ''.join(upper(char) for char in list(string))


def upper(char):
    """Upcode a char"""

    if ord(char) < 32 or char == ':':
        return '%' + chr(64+ord(char))
    elif char == '%':
        return '%%'
    else:
        return char


if __name__ == '__main__':
    try:
        YateScript().run()
    except KeyboardInterrupt:
        pass
