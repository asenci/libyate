"""
libyate.py - Python library for developing Yate external modules


Copyright (c) 2013 Andre Sencioles Vitorio Oliveira <andre@bcp.net.br>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
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

    # class attributes
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

        # Initialize empty parameters
        elif cmd is None:
            for param in self.__params__:
                if param == 'kvp':
                    setattr(self, param, {})
                else:
                    setattr(self, param, '')

        # Invalid parameter
        else:
            raise TypeError('Invalid type for "cmd": {0}'.format(type(cmd)))

        # Override parameters from kwargs
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

    # class attributes
    __method__ = KW_CONNECT
    __params__ = ('method', 'role', 'id', 'type')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'connect/{0}'.format(self.role)


class YateCmdError(YateCmd):
    """Yate output command"""

    # class attributes
    __method__ = KW_ERROR
    __params__ = ('method', 'original')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'error/{0}'.format(self.original)


class YateCmdInstall(YateCmd):
    """Yate install command"""

    # class attributes
    __method__ = KW_INSTALL
    __params__ = ('method', 'priority', 'name', 'filter_name', 'filter_value')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'install/{0}'.format(self.name)


class YateCmdInstallReply(YateCmd):
    """Yate install reply command"""

    # class attributes
    __method__ = KW_INSTALLREPLY
    __params__ = ('method', 'priority', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'install/{0}'.format(self.name)


class YateCmdMessage(YateCmd):
    """Yate message command"""

    # class attributes
    __method__ = KW_MESSAGE
    __params__ = ('method', 'id', 'time', 'name', 'retvalue', 'kvp')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        # Generate a random ID if not already defined
        if not self.id:
            self.id = id(self)

        self.__id__ = 'message/{0}'.format(self.id)

    def reply(self, **kwargs):
        return YateCmdMessageReply(self, **kwargs)


class YateCmdMessageReply(YateCmd):
    """Yate message reply command"""

    # class attributes
    __method__ = KW_MESSAGEREPLY
    __params__ = ('method', 'id', 'processed', 'name', 'retvalue', 'kvp')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'message/{0}'.format(self.id)


class YateCmdOutput(YateCmd):
    """Yate output command"""

    # class attributes
    __method__ = KW_OUTPUT
    __params__ = ('method', 'output')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'output/{0}'.format(self.output)


class YateCmdSetLocal(YateCmd):
    """Yate setlocal command"""

    # class attributes
    __method__ = KW_SETLOCAL
    __params__ = ('method', 'name', 'value')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'setlocal/{0}'.format(self.name)


class YateCmdSetLocalReply(YateCmd):
    """Yate setlocal reply command"""

    # class attributes
    __method__ = KW_SETLOCALREPLY
    __params__ = ('method', 'name', 'value', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'setlocal/{0}'.format(self.name)


class YateCmdUnInstall(YateCmd):
    """Yate uninstall command"""

    # class attributes
    __method__ = KW_UNINSTALL
    __params__ = ('method', 'name')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'uninstall/{0}'.format(self.name)


class YateCmdUnInstallReply(YateCmd):
    """Yate uninstall reply command"""

    # class attributes
    __method__ = KW_UNINSTALLREPLY
    __params__ = ('method', 'priority', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'uninstall/{0}'.format(self.name)


class YateCmdUnWatch(YateCmd):
    """Yate unwatch command"""

    # class attributes
    __method__ = KW_UNWATCH
    __params__ = ('method', 'name')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'unwatch/{0}'.format(self.name)


class YateCmdUnWatchReply(YateCmd):
    """Yate unwatch reply command"""

    # class attributes
    __method__ = KW_UNWATCHREPLY
    __params__ = ('method', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'unwatch/{0}'.format(self.name)


class YateCmdWatch(YateCmd):
    """Yate watch command"""

    # class attributes
    __method__ = KW_WATCH
    __params__ = ('method', 'name')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'watch/{0}'.format(self.name)


class YateCmdWatchReply(YateCmd):
    """Yate watch reply command"""

    # class attributes
    __method__ = KW_WATCHREPLY
    __params__ = ('method', 'name', 'success')

    def __init__(self, cmd=None, **kwargs):
        YateCmd.__init__(self, cmd=cmd, **kwargs)

        self.__id__ = 'watch/{0}'.format(self.name)


class YateExtModule(object):
    """Yate external module"""

    def __init__(self, name=__name__, debug=False, quiet=False):
        """Initialize the class"""

        import logging
        from Queue import Queue

        log_format = \
            '%(asctime)s <%(name)s[%(threadName)s]:%(levelname)s> %(message)s'

        logging.basicConfig(**{
            'level': (logging.DEBUG if debug else
                      logging.WARN if quiet else
                      logging.INFO),
            'format': log_format,
        })

        # Logger instance
        self.logger = logging.getLogger(name)

        # Instance name
        self.name = name

        # Command queue
        self.cmd_queue = {}

        # Input queue
        self.in_queue = Queue()

        # Output queue
        self.out_queue = Queue()

    def connect(self, role, **kwargs):
        """Attach to the socket interface"""

        self.logger.debug('Connecting: "{0}"'.format(role))

        self.out_queue.put(YateCmdConnect(role=role, **kwargs))

    def handle_command(self, cmd):
        """Inbound command handler"""

        self.logger.debug('Processing command: {0}'.format(cmd))
        try:
            # Reply
            if cmd.__method__.startswith('%%<'):

                # Find initial command
                orig = self.cmd_queue.pop(cmd.__id__)

                if orig:
                    if orig(cmd):
                        self.logger.debug(
                            'Command executed successfully: {0}'.format(orig))
                    else:
                        self.logger.error(
                            'Error executing command: {0}'.format(orig))
                else:
                    self.logger.debug(
                        'Original command not fount for reply: {0}'
                        .format(cmd))

            # Error
            elif cmd.__method__ == KW_ERROR:
                self.logger.error(
                    'Invalid command: {0}'.format(cmd.original))

                # Try to remove original message from the queue
                self.cmd_queue.pop(YateCmd(cmd.original).__id__)

            # New message
            elif cmd.__method__ == KW_MESSAGE:
                self.logger.debug(
                    'No action defined, replying without processing')
                self.out_queue.put(cmd.reply())

        # Command not found on command queue dictionary
        except KeyError as e:
            self.logger.error('ID not found on command queue: {0}'.format(e))

        # Log exceptions
        except Exception as e:
            self.logger.error(e)

    def handle_input(self, queue):
        """Input queue handler"""

        from threading import Thread
        from time import sleep

        self.logger.info('Starting')

        # Initialize thread list
        handler_list = []

        # Initial state
        running = True

        # Main loop
        while running:
            try:
                # Get next command from the queue
                cmd = queue.get()
                self.logger.debug(
                    'Received command: {0}'.format(cmd))

                # CLeanup thread list
                while running:

                    # Remove finished threads
                    for i, t in enumerate(handler_list):
                        if not t.is_alive():
                            handler_list.pop(i)
                            self.logger.debug(
                                'Removed finished thread: {0}'.format(t.name))

                    # Command defined
                    if cmd:

                        # Start a new handler thread
                        t = Thread(
                            target=self.handle_command,
                            args=(cmd,),
                            name=cmd.__id__,
                        )
                        self.logger.debug(
                            'Starting handler: {0}'.format(t.name))
                        t.start()

                        # Append thread to the list
                        handler_list.append(t)

                        # Stop cleanup
                        break

                    # Handler list not empty
                    elif handler_list:

                        # Wait for threads to finish
                        sleep(0.1)

                    # Command not defined and handler list empty
                    else:

                        # Start shutdown sequence
                        running = False

            # Log exceptions
            except Exception as e:
                self.logger.error(e)

        self.logger.info('Finished')

    def handle_output(self, queue):
        """Output queue handler"""

        import sys

        self.logger.info('Starting')

        # Initial state
        running = True

        # Main loop
        while running:

            try:
                # Get next command from the queue
                cmd = queue.get()
                self.logger.debug(
                    'Received command: {0}'.format(cmd))

                # Command defined
                if cmd:

                    # Send command to the engine
                    self.logger.debug('Sending: {0}'.format(cmd))
                    sys.stdout.write('{0}\n'.format(cmd))

                    # Flush buffer
                    sys.stdout.flush()

                # Command not defined
                else:

                    # Start shutdown sequence
                    running = False

            # Log exceptions
            except Exception as e:
                self.logger.error(e)

        self.logger.info('Finished')

    def handle_start(self):
        """Module startup handler"""

        self.logger.debug('Module startup')

    def handle_stop(self):
        """Module shutdown handler"""

        self.logger.debug('Module shutdown')

    def install(self, name, **kwargs):
        """Install message handler"""

        self.logger.debug('Installing handler for "{0}"'.format(name))

        cmd = YateCmdInstall(name=name, **kwargs)

        self.cmd_queue.update({cmd.__id__: cmd})
        self.out_queue.put(cmd)

    def message(self, name, **kwargs):
        """Send message to Yate"""

        self.logger.debug('Sending message: "{0}"'.format(name))

        cmd = YateCmdMessage(name=name, **kwargs)

        self.cmd_queue.update({cmd.__id__: cmd})
        self.out_queue.put(cmd)

    def output(self, output):
        """Send message to Yate"""

        self.logger.debug('Sending output: "{0}"'.format(output))

        self.out_queue.put(YateCmdOutput(output=output))

    def run(self):
        """Start processing commands"""

        import sys
        from threading import Thread

        self.logger.info('Loading module')

        # Initial state
        running = True

        # Start output queue handler
        self.logger.debug('Starting output queue handler')
        out_handler = Thread(
            target=self.handle_output,
            args=(self.out_queue,),
            name='OutputHandler'
        )
        out_handler.start()

        # Start input queue handler
        self.logger.debug('Starting input queue handler')
        in_handler = Thread(
            target=self.handle_input,
            args=(self.in_queue,),
            name='InputHandler'
        )
        in_handler.start()

        # Startup routine
        self.logger.debug('Running startup handler')
        self.handle_start()

        # Main loop
        self.logger.debug('Entering main loop')
        while running:

            # Process incoming commands
            try:
                line = sys.stdin.readline()

                if line:
                    line = line.rstrip('\n')

                    self.logger.debug('Received: {0}'.format(line))

                    self.in_queue.put(YateCmd(line))

                else:
                    raise EOFError

            # Shutdown routine
            except (KeyboardInterrupt, EOFError):

                # Shutdown handler
                self.logger.info('Running shutdown handler')
                self.handle_stop()

                # Shutdown input queue handler
                self.logger.debug('Shutting down input queue')
                self.in_queue.put(None)
                self.logger.debug('Waiting for input queue handler')
                in_handler.join()

                # Shutdown output queue handler
                self.logger.debug('Shutting down output queue')
                self.out_queue.put(None)
                self.logger.debug('Waiting for output queue handler')
                out_handler.join()

                # Start shutdown sequence
                running = False

            # Log exceptions
            except Exception as e:
                self.logger.error(e)

    def set_local(self, name, value):
        """Set module local parameters"""

        self.logger.debug('Setting parameter "{0}": "{1}"'.format(name, value))

        cmd = YateCmdSetLocal(name=name, value=value)

        self.cmd_queue.update({cmd.__id__: cmd})
        self.out_queue.put(cmd)

    def uninstall(self, name):
        """Uninstall message handler"""

        self.logger.debug('Uninstalling handler for "{0}"'.format(name))

        cmd = YateCmdUnInstall(name=name)

        self.cmd_queue.update({cmd.__id__: cmd})
        self.out_queue.put(cmd)

    def unwatch(self, name):
        """Uninstall message watcher"""

        self.logger.debug('Uninstalling watcher for "{0}"'.format(name))

        cmd = YateCmdUnWatch(name=name)

        self.cmd_queue.update({cmd.__id__: cmd})
        self.out_queue.put(cmd)

    def watch(self, name):
        """Install message watcher"""

        self.logger.debug('Installing watcher for "{0}"'.format(name))

        cmd = YateCmdWatch(name=name)

        self.cmd_queue.update({cmd.__id__: cmd})
        self.out_queue.put(cmd)


class YateSocketClient(YateExtModule):
    """Socket connected external module"""

    # TODO: implement SocketClient class
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
