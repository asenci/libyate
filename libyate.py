"""
libyate.py - Python library for developing Yate external modules
"""

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


class YateCmd(object):
    """Object representing an Yate command"""

    # Internal attributes
    __id__ = ''
    __method__ = ''
    __params__ = ()

    def __new__(cls, cmd=None, **kwargs):
        """Return a Yate command object from a command string"""

        if cls != YateCmd:
            return super(YateCmd, cls).__new__(cls)

        else:

            if isinstance(cmd, str):
                method = cmd.partition(':')[0]
            elif isinstance(cmd, YateCmd):
                method = cmd.__method__
            else:
                method = kwargs.get('method', '')

            if method == KW_CONNECT:
                return super(YateCmd, cls).__new__(YateCmdConnect)

            elif method == KW_ERROR:
                return super(YateCmd, cls).__new__(YateCmdError)

            elif method == KW_INSTALL:
                return super(YateCmd, cls).__new__(YateCmdInstall)

            elif method == KW_INSTALLREPLY:
                return super(YateCmd, cls).__new__(YateCmdInstallReply)

            elif method == KW_MESSAGE:
                return super(YateCmd, cls).__new__(YateCmdMessage)

            elif method == KW_MESSAGEREPLY:
                return super(YateCmd, cls).__new__(YateCmdMessageReply)

            elif method == KW_OUTPUT:
                return super(YateCmd, cls).__new__(YateCmdOutput)

            elif method == KW_SETLOCAL:
                return super(YateCmd, cls).__new__(YateCmdSetLocal)

            elif method == KW_SETLOCALREPLY:
                return super(YateCmd, cls).__new__(YateCmdSetLocalReply)

            elif method == KW_UNINSTALL:
                return super(YateCmd, cls).__new__(YateCmdUnInstall)

            elif method == KW_UNINSTALLREPLY:
                return super(YateCmd, cls).__new__(YateCmdUnInstallReply)

            elif method == KW_UNWATCH:
                return super(YateCmd, cls).__new__(YateCmdUnWatch)

            elif method == KW_UNWATCHREPLY:
                return super(YateCmd, cls).__new__(YateCmdUnWatchReply)

            elif method == KW_WATCH:
                return super(YateCmd, cls).__new__(YateCmdWatch)

            elif method == KW_WATCHREPLY:
                return super(YateCmd, cls).__new__(YateCmdWatchReply)

            else:
                raise NotImplementedError(
                    'Command method "{0}" not implemented'.format(method))

    def __init__(self, cmd=None, **kwargs):
        """Init object from command line, YateCmd object or dict"""
        from datetime import datetime

        # Initialize from a command string
        if isinstance(cmd, str):

            for param in self.__params__:

                # No parameters left
                if not cmd:
                    value = ''

                # Raw strings
                elif param in ['original', 'output']:
                    value = cmd

                # Command method, don't downcode
                elif param == 'method':
                    value, cmd = cmd.partition(':')[::2]

                # Convert a (true|false) string into a boolean
                elif param in ['processed', 'success']:
                    value, cmd = cmd.partition(':')[::2]
                    value = value == 'true'

                # Convert a string into a integer
                elif param == 'priority':
                    value, cmd = cmd.partition(':')[::2]
                    if value:
                        value = int(value)

                # Convert a timestamp string into a datetime object
                elif param == 'time':
                    value, cmd = cmd.partition(':')[::2]
                    if value:
                        value = datetime.fromtimestamp(int(value))

                # Key-value pairs
                elif param == 'kvp':

                    # Copy the instance dictionary or initialize a new one
                    value = getattr(self, param, {}).copy()

                    # Update the dictionary items
                    for kvp in cmd.split(':'):
                        k, v = kvp.partition('=')[::2]

                        if k:
                            value.update({downcode(k): downcode(v)})

                # Other parameters, downcode string characters
                else:
                    value, cmd = cmd.partition(':')[::2]
                    value = downcode(value)

                # Save instance attribute
                setattr(self, param, value)

        # Initialize from another Yate command object
        elif isinstance(cmd, YateCmd):
            for param in self.__params__:

                # Update key-value dictionary
                if param == 'kvp':

                    # Get instance dictionary
                    kvp = getattr(self, param, {})

                    # Update the instance dictionary
                    kvp.update(getattr(cmd, param, {}))

                    # Save the instance dictionary
                    setattr(self, param, kvp)

                # Copy parameter
                else:
                    setattr(self, param, getattr(cmd, param, ''))

        if kwargs:
            for param in self.__params__:

                # Update key-value dictionary
                if param == 'kvp':

                    # Get instance dictionary
                    kvp = getattr(self, param, {})

                    # Update the instance dictionary
                    kvp.update(kwargs.get(param, {}))

                    # Save the instance dictionary
                    setattr(self, param, kvp)

                # Copy parameter
                else:
                    value = kwargs.get(param, '')
                    if value:
                        setattr(self, param, kwargs.get(param, ''))

    def __call__(self, reply=None):
        """Handle the command reply"""

        # Message command does not support success indication
        if reply.__method__ == KW_MESSAGEREPLY:
            return True

        # Return command execution result
        else:
            return getattr(reply, 'success', False)

    def __repr__(self):
        return '{0}(\'{1}\')'.format(self.__class__.__name__, self)

    def __str__(self):
        """Convert object into a command line"""
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        """Convert object into a command line"""
        from datetime import datetime

        # Create a empty list to store the command parameters
        cmd = [self.__method__]

        # Get the command parameters
        for param in self.__params__:

            # Method already defined
            if param == 'method':
                continue

            # Not encoded parameters, just convert to string
            elif param in ['original', 'output']:
                value = getattr(self, param, '')

            # Convert a boolean into a (true|false) string (defaults to false)
            elif param in ['processed', 'success']:
                value = 'true' if getattr(self, param, False) else 'false'

            # Convert a datetime object into a timestamp (defaults to now)
            elif param == 'time':
                value = getattr(self, param, '')
                if isinstance(value, datetime):
                    value = value.strftime('%s')
                else:
                    value = datetime.now().strftime('%s')

            # Key-value pairs
            elif param == 'kvp':
                value = ':'.join((
                    '='.join((upcode(k), upcode(v)))
                    for k, v in self.kvp.iteritems()
                ))

            # Other parameters, downcode string characters
            else:
                value = upcode(getattr(self, param, ''))

            # Append parameter value to the list
            cmd.append(value)

        return ':'.join(cmd).rstrip(':')


class YateCmdConnect(YateCmd):
    """Yate connect command"""

    __method__ = KW_CONNECT
    __params__ = ('method', 'role', 'id', 'type')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'connect/{0}'.format(self.role)


class YateCmdError(YateCmd):
    """Yate output command"""

    __method__ = KW_ERROR
    __params__ = ('method', 'original',)

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'error/{0}'.format(self.original)


class YateCmdInstall(YateCmd):
    """Yate install command"""

    __method__ = KW_INSTALL
    __params__ = ('method', 'priority', 'name', 'filter_name', 'filter_value')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'install/{0}'.format(self.name)


class YateCmdInstallReply(YateCmd):
    """Yate install reply command"""

    __method__ = KW_INSTALLREPLY
    __params__ = ('method', 'priority', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'install/{0}'.format(self.name)


class YateCmdMessage(YateCmd):
    """Yate message command"""

    __method__ = KW_MESSAGE
    __params__ = ('method', 'id', 'time', 'name', 'retvalue', 'kvp')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        # Generate a random ID if not already defined
        if not self.id:
            self.id = id(self)

        self.__id__ = 'message/{0}'.format(self.id)


class YateCmdMessageReply(YateCmd):
    """Yate message reply command"""

    __method__ = KW_MESSAGEREPLY
    __params__ = ('method', 'id', 'processed', 'name', 'retvalue', 'kvp')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'message/{0}'.format(self.id)


class YateCmdOutput(YateCmd):
    """Yate output command"""

    __method__ = KW_OUTPUT
    __params__ = ('method', 'output',)

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'output/{0}'.format(self.output)


class YateCmdSetLocal(YateCmd):
    """Yate setlocal command"""

    __method__ = KW_SETLOCAL
    __params__ = ('method', 'name', 'value')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'setlocal/{0}'.format(self.name)


class YateCmdSetLocalReply(YateCmd):
    """Yate setlocal reply command"""

    __method__ = KW_SETLOCALREPLY
    __params__ = ('method', 'name', 'value', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'setlocal/{0}'.format(self.name)


class YateCmdUnInstall(YateCmd):
    """Yate uninstall command"""

    __method__ = KW_UNINSTALL
    __params__ = ('method', 'name',)

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'uninstall/{0}'.format(self.name)


class YateCmdUnInstallReply(YateCmd):
    """Yate uninstall reply command"""

    __method__ = KW_UNINSTALLREPLY
    __params__ = ('method', 'priority', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'uninstall/{0}'.format(self.name)


class YateCmdUnWatch(YateCmd):
    """Yate unwatch command"""

    __method__ = KW_UNWATCH
    __params__ = ('method', 'name',)

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'unwatch/{0}'.format(self.name)


class YateCmdUnWatchReply(YateCmd):
    """Yate unwatch reply command"""

    __method__ = KW_UNWATCHREPLY
    __params__ = ('method', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'unwatch/{0}'.format(self.name)


class YateCmdWatch(YateCmd):
    """Yate watch command"""

    __method__ = KW_WATCH
    __params__ = ('method', 'name',)

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'watch/{0}'.format(self.name)


class YateCmdWatchReply(YateCmd):
    """Yate watch reply command"""

    __method__ = KW_WATCHREPLY
    __params__ = ('method', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'watch/{0}'.format(self.name)


class YateExtModule(object):
    """Yate external module"""

    def __init__(self, name=__name__, debug=False, quiet=False):
        """Initialize the class, optionally overriding the handlers map"""
        import logging

        logging.basicConfig(**{
            'level': (logging.DEBUG if debug else
                      logging.WARN if quiet else
                      logging.INFO),
            'format': '%(created)f <%(name)s:%(levelname)s> %(message)s',
        })

        self.name = name
        self.debug = debug
        self.logger = logging.getLogger(self.name)
        self.queue = {}

    def _read(self):
        """Read commands from stdin"""

        line = raw_input()

        self.logger.debug('Received: {0}'.format(line))

        return YateCmd(line)

    def _write(self, cmd):
        """Write commands to stdout"""
        import sys

        self.logger.debug('Sending: {0}'.format(cmd))

        print(cmd)
        sys.stdout.flush()

    def handle_input(self, cmd):
        """Command input handler"""

        # New message
        if cmd.__method__ == KW_MESSAGE:

            # Process and send reply
            self.send(self.handle_message(cmd))

        # Command error
        elif cmd.__method__ == KW_ERROR:
            self.logger.error('Invalid command: {0}'.format(cmd.original))

            # Try to remove original message from the queue
            self.queue_pop(YateCmd(cmd.original))

        # Command reply
        else:
            self.handle_reply(cmd)

    def handle_message(self, cmd):
        """Stub message handler"""

        # Reply without processing
        return YateCmdMessageReply(cmd)

    def handle_reply(self, reply):
        """Command reply handler"""

        # Retrieve the command from the queue
        cmd = self.queue_pop(reply)

        if cmd:
            # Send the reply to the command instance
            if cmd(reply):
                self.logger.debug(
                    'Command executed successfully: {0}'.format(cmd))
            else:
                self.logger.error('Error executing command: {0}'.format(cmd))

    def on_start(self):
        """Startup hook"""
        self.logger.debug('Running startup hook')

        # Set local variables
        self.send(YateCmdSetLocal(name='restart', value='true'))

        # Register hooks
        self.send(YateCmdWatch(name='engine.timer'))

    def on_stop(self):
        """Exit hook"""
        self.logger.debug('Running exit hook')

        # Set local variables
        self.send(YateCmdSetLocal(name='restart', value='false'))

        # Unregister hooks
        self.send(YateCmdUnWatch(name='engine.timer'))

    def queue_pop(self, cmd):
        """Retrieve a command from the queue"""

        # Remove the command from the queue if present
        return self.queue.pop(cmd.__id__, None)

    def queue_push(self, cmd):
        """Insert a command into the queue"""

        self.queue.update({cmd.__id__: cmd})

    def run(self):
        """Main loop"""
        self.logger.debug('Loading module')
        self.on_start()

        self.logger.debug('Entering main loop')
        # Loop until interrupted
        while True:
            # Queue size for debugging
            self.logger.debug('Queue size: {0}'.format(len(self.queue)))

            # Process incoming commands
            try:
                self.handle_input(self._read())

            # Exit hook
            except (KeyboardInterrupt, EOFError):
                self.on_stop()
                break

            # Intercept exceptions and log the error if debugging is disable
            except (None if self.debug else Exception), e:
                self.logger.error(e)

    def send(self, cmd):
        """Command output handler"""

        # Store command into the queue so we can handle the reply
        if cmd.__method__ in [KW_INSTALL, KW_MESSAGE, KW_SETLOCAL,
                              KW_UNINSTALL, KW_UNWATCH, KW_WATCH]:
            self.queue_push(cmd)

        # Send the command
        self._write(cmd)


class YateSocketClient(YateExtModule):
    """Socket connected external module"""
    #TODO: implement SocketClient class
    pass


def downcode(string):
    """Decode Yate upcoded strings"""

    # Init empty list
    result = []

    # First char is not upcoded
    upcoded = False

    for c in str(string):
        # Check if this char is upcoded
        if upcoded:
            # Next char is not upcoded
            upcoded = False

            if c == '%':
                result.append('%')
            else:
                result.append(chr(ord(c) - 64))
        else:
            if c == '%':
                upcoded = True
            else:
                result.append(c)

    return ''.join(result)


def upcode(string, special=':'):
    """Encode string into Yate upcoded"""

    # Init empty list
    result = []

    for c in str(string):
        if ord(c) < 32 or c in special:
            result.append('%{0:c}'.format(ord(c) + 64))
        elif c == '%':
            result.append('%%')
        else:
            result.append(c)

    return ''.join(result)
