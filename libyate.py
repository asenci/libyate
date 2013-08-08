#!/usr/bin/env python

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
    KW_CONNECT: ['role', 'id', 'type'],
    KW_ERROR: ['command'],
    KW_INSTALL: ['priority', 'name', 'filtername', 'filtervalue'],
    KW_INSTALLREPLY: ['priority', 'name', 'success'],
    KW_MESSAGE: ['id', 'timestamp', 'name', 'retval', 'extras'],
    KW_MESSAGEREPLY: ['id', 'processed', 'name', 'retval', 'extras'],
    KW_OUTPUT: ['output'],
    KW_SETLOCAL: ['name', 'value'],
    KW_SETLOCALREPLY: ['name', 'value', 'success'],
    KW_UNINSTALL: ['name'],
    KW_UNINSTALLREPLY: ['priority', 'name', 'success'],
    KW_UNWATCH: ['name'],
    KW_UNWATCHREPLY: ['name', 'success'],
    KW_WATCH: ['name'],
    KW_WATCHREPLY: ['name', 'success'],
}


class YateCmd(object):
    """Object representing an Yate command"""

    def __init__(self, cmd=None, **kwargs):
        """Init object from command line, YateCmd object or dict"""
        from datetime import datetime

        extras = getattr(self, 'extras', {})

        # Init from another YateCmd object
        if isinstance(cmd, YateCmd):

            # Copy the attributes
            attr = cmd.__dict__.copy()

            # Update the extra parameters
            extras.update(attr.pop('extras', {}))

            self.__dict__.update(attr)

        # Init from a command line
        elif isinstance(cmd, str):

            # Get method from the command line
            try:
                self.method, cmd = cmd.split(':', 1)
            except ValueError:
                raise SyntaxError('Invalid command: {0}'.format(cmd))

            # Get parameter from the command line
            for attr in self.attrs():

                # Get next parameter value
                if ':' in cmd and attr not in ['command', 'extras', 'output']:
                    value, cmd = cmd.split(':', 1)
                # Last parameter on the command line
                elif cmd:
                    value = cmd
                    cmd = ''
                # No parameters left on the command line
                else:
                    break

                # Not encoded strings
                if attr in ['command', 'output']:
                    setattr(self, attr, value)

                # Convert a (true|false) string into a boolean
                elif attr in ['processed', 'success']:
                    setattr(self, attr, (True if value == 'true' else False))

                # Convert a string into a integer
                elif attr == 'priority':
                    setattr(self, attr, int(value))

                # Convert a timestamp string into a datetime object
                elif attr == 'timestamp':
                    setattr(self, attr, datetime.fromtimestamp(int(value)))

                # Extra parameters
                elif attr == 'extras':

                    # Get all remaining parameters
                    value += cmd

                    # Update the extra parameters with the param-value pairs
                    extras.update(
                        ((self.downcode(x), self.downcode(y))
                         for x, y in (z.split('=', 1)
                         for z in value.split(':')))
                    )

                # Other parameters, decode the string (downcode the characters)
                else:
                    setattr(self, attr, self.downcode(value))

        # Update the parameters from the supplied attributes
        if kwargs:

            # Update the extra parameters
            extras.update(kwargs.pop('extras', {}))

            # Update the attributes
            self.__dict__.update(**kwargs)

        # Store the extra parameters
        self.extras = extras

        # Command identifier for queue processing
        self.key = getattr(self, 'name', id(self))

    def __call__(self, reply=None):
        """Handle the command reply"""

        # Message command does not support success indication
        if reply.method == KW_MESSAGEREPLY:
            return True
        # Command executed successfully
        elif getattr(reply, 'success', False):
            return True
        # Error executing the command
        else:
            return False

    def __repr__(self):
        method = getattr(self, 'method', None)

        if method in [KW_MESSAGE, KW_MESSAGEREPLY]:
            key = getattr(self, 'id', id(self))
        else:
            key = getattr(self, 'name', id(self))

        if method == KW_ERROR:
            method = 'error'
        elif method:
            method = method[3:]
        else:
            method = 'blank'

        return '<YateCmd {0} {1}>'.format(method, key)

    def __str__(self):
        """Convert object into a command line"""
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        """Convert object into a command line"""
        from datetime import datetime

        # In    it a new list to store the command parameters
        reply = [self.method]

        # Get the command parameters from the object attributes
        for attr in self.attrs():

            # Not encoded parameters, just convert to string
            if attr in ['command', 'output']:
                reply.append(getattr(self, attr, '') or '')

            # Convert a boolean into a (true|false) string (defaults to false)
            elif attr in ['processed', 'success']:
                reply.append('true' if getattr(self, attr, False) else 'false')

            # Convert a datetime object into a timestamp (defaults to now)
            elif attr == 'timestamp':
                reply.append(getattr(self, attr, datetime.now()).strftime('%s'))

            # Extra parameters
            elif attr == 'extras':
                for attr, value in getattr(self, attr, {}).iteritems():
                    reply.append(
                        '='.join((self.upcode(attr), self.upcode(value))))

            # Other parameters, encode the string (upcode the characters)
            else:
                reply.append(self.upcode(getattr(self, attr, '') or ''))

        return ':'.join(reply).rstrip(':')

    def attrs(self):
        try:
            return KW_MAP[self.method]
        except KeyError:
            raise NotImplementedError(
                'Method "{0}" not implemented'.format(self.method))
        except AttributeError:
            raise SyntaxError('Method not defined')

    @staticmethod
    def downcode(string, upcoded=False):
        """Decode Yate upcoded strings"""

        # Init empty list
        result = []

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

    @staticmethod
    def upcode(string, special=(':', '=')):
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


class YateCmdConnect(YateCmd):
    """Yate connect command"""

    def __init__(self, role, id=None, type=None, method=KW_CONNECT):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdInstall(YateCmd):
    """Yate install command"""

    def __init__(self, name, priority=None, filtername=None, filtervalue=None,
                 method=KW_INSTALL):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdMessage(YateCmd):
    """Yate message command"""

    def __init__(self, name, id=None, timestamp=None, retval=None, extras=None,
                 method=KW_MESSAGE):

        if not id:
            id = id(self)

        if not timestamp:
            from datetime import datetime
            timestamp = datetime.now()

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdMessageReply(YateCmd):
    """Yate message reply command"""

    def __init__(self, cmd, method=KW_MESSAGEREPLY):

        # Run the init code
        YateCmd.__init__(self, cmd, method=method)


class YateCmdOutput(YateCmd):
    """Yate output command"""

    def __init__(self, output, method=KW_OUTPUT):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdSetLocal(YateCmd):
    """Yate setlocal command"""

    def __init__(self, name, value, method=KW_SETLOCAL):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdUnInstall(YateCmd):
    """Yate uninstall command"""

    def __init__(self, name, method=KW_UNINSTALL):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdUnWatch(YateCmd):
    """Yate unwatch command"""

    def __init__(self, name,  method=KW_UNWATCH):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


class YateCmdWatch(YateCmd):
    """Yate watch command"""

    def __init__(self, name, method=KW_WATCH):

        # Parameters
        kwargs = locals().copy()
        kwargs.pop('self')

        # Run the init code
        YateCmd.__init__(self, **kwargs)


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

        self.logger.debug('Sending: {0}'.format(cmd))

        print(cmd)

    def handle_input(self, cmd):
        """Command input handler"""

        # New message
        if cmd.method == KW_MESSAGE:
            self.handle_message(cmd)

        # Command error
        elif cmd.method == KW_ERROR:
            self.logger.error('Invalid command: {0}'.format(cmd.command))

            # Try to remove original message from the queue
            self.queue_pop(YateCmd(cmd.command))

        # Command reply
        else:
            self.handle_reply(cmd)

    def handle_message(self, cmd):
        """Stub message handler"""

        # Reply without processing
        self.send(YateCmdMessageReply(cmd))

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
        self.send(YateCmdSetLocal('restart', 'true'))

        # Register hooks
        self.send(YateCmdWatch('engine.timer'))

    def on_stop(self):
        """Exit hook"""
        self.logger.debug('Running exit hook')

        # Set local variables
        self.send(YateCmdSetLocal('restart', 'false'))

        # Unregister hooks
        self.send(YateCmdUnWatch('engine.timer'))

    def queue_pop(self, cmd):
        """Retrieve a command from the queue"""

        # Remove the command from the queue if present
        return self.queue.pop(repr(cmd), {})

    def queue_push(self, cmd):
        """Insert a command into the queue"""

        self.queue[repr(cmd)] = cmd

    def run(self):
        """Main loop"""
        self.logger.info('Loading module')
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
                self.logger.error(e.message)

    def send(self, cmd):
        """Command output handler"""

        # Store command into the queue so we can handle the reply
        if cmd.method in [KW_INSTALL, KW_MESSAGE, KW_SETLOCAL,
                          KW_UNINSTALL, KW_UNWATCH, KW_WATCH]:
            self.queue_push(cmd)

        # Send the command
        self._write(cmd)


class YateSocketClient(YateExtModule):
    """Socket connected external module"""
    #TODO: implement SocketClient class
    pass


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true',
                      help='increase logging verbosity')
    parser.add_option('-q', '--quiet', action='store_true',
                      help='reduce the logging verbosity')
    parser.add_option('-n', '--name', default=__file__,
                      help='name used for logging')

    YateExtModule(**vars(parser.parse_args()[0])).run()
