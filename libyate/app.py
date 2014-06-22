"""
libyate - application code
"""

import libyate
import libyate.cmd


class YateExtScript(object):
    """External script"""

    def __init__(self, name=None):
        import logging
        from Queue import Queue

        # Instance name
        if name is None:
            self.__name__ = name or self.__class__.__name__
        else:
            self.__name__ = name

        # Message handlers
        self.__msg_callback__ = {}
        self.__msg_handlers__ = {}
        self.__msg_watchers__ = {}

        # Logger instance
        self.logger = logging.getLogger(self.__name__)

        # Output queue
        self._output = Queue()

    def run(self):
        """User defined startup function"""

    def start(self):
        """Start main loop and wait for commands"""

        from sys import stdin
        from threading import Thread

        self.logger.info('Starting module')
        Thread(target=self.on_start, name='StartupThread').start()

        # Main loop
        self.logger.debug('Started input')
        while True:

            # Process incoming commands
            try:
                line = stdin.readline()

                if line:
                    line = line.rstrip('\n')
                    self.logger.debug('Received: {0}'.format(line))

                    # Start a new handler thread
                    cmd_obj = libyate.cmd_from_string(line)
                    Thread(target=self.on_command, args=(cmd_obj,),
                           name='{0}({1})'.format(type(cmd_obj).__name__,
                                                  id(cmd_obj))).start()

                else:
                    raise EOFError

            # Interrupt main loop
            except (EOFError, IOError, KeyboardInterrupt, SystemExit):
                self.logger.info('Stopped input')
                break

            # Log exceptions
            except:
                self.logger.exception('Error reading from stdin')

        self.logger.debug('Waiting for threads')

    def send(self, command):
        self._output.put(command)

    def on_start(self):
        """Module startup routine"""

        from threading import Thread

        # Start the output handler thread
        self.logger.debug('Starting output handler thread')
        t = Thread(target=self.on_output, name='OutputThread')
        t.daemon = True
        t.start()

        # Execute user code
        self.logger.debug('Executing user code')
        self.run()

    def on_command(self, cmd_obj):
        """Command handler"""

        self.logger.debug('Received command: {0!r}'.format(cmd_obj))

        try:
            if isinstance(cmd_obj, (libyate.cmd.Message,
                                    libyate.cmd.MessageReply)):

                # Message from installed handlers
                if isinstance(cmd_obj, libyate.cmd.Message):
                    handler = self.__msg_handlers__[cmd_obj.name]

                # Reply from application generated message
                elif cmd_obj.id is not None:
                    handler = self.__msg_callback__.pop(cmd_obj.id)

                # Notification from installed watchers
                else:
                    handler = self.__msg_watchers__[cmd_obj.name]

                self.logger.debug('Handler: {0}'.format(handler))
                result = handler(cmd_obj)

                self.logger.debug('Result: {0}'.format(result))
                if result is not None:
                    self.send(result)

            elif isinstance(cmd_obj, libyate.cmd.Error):
                self.logger.error('Invalid command: {0}'
                                  .format(cmd_obj.original))

            elif isinstance(cmd_obj, libyate.cmd.InstallReply):
                if cmd_obj.success:
                    self.logger.info('Installed handler for "{0}"'
                                     .format(cmd_obj.name))
                else:
                    self.logger.error('Error installing handler for "{0}"'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.SetLocalReply):
                if cmd_obj.success:
                    self.logger.info('Parameter "{0}" set to: {1}'
                                     .format(cmd_obj.name, cmd_obj.value))
                else:
                    self.logger.error('Error setting parameter "{0}"'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.UnInstallReply):
                if cmd_obj.success:
                    self.logger.info('Removed handler for "{0}"'
                                     .format(cmd_obj.name))
                else:
                    self.logger.error('Error removing handler for "{0}"'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.UnWatchReply):
                if cmd_obj.success:
                    self.logger.info('Removed watcher for "{0}"'
                                     .format(cmd_obj.name))
                else:
                    self.logger.error('Error removing watcher for "{0}"'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.WatchReply):
                if cmd_obj.success:
                    self.logger.info('Installed watcher for "{0}"'
                                     .format(cmd_obj.name))
                else:
                    self.logger.error('Error installing watcher for "{0}"'
                                      .format(cmd_obj.name))

            else:
                self.logger.critical('No handler defined for "{0}" command'
                                     .format(type(cmd_obj).__name__))

        except:
            self.logger.exception('Error processing command: {0}'
                                  .format(cmd_obj))

    def on_output(self):
        """Output queue handler"""
        from sys import stdout

        self.logger.debug('Started output')

        # Main loop
        while True:

            # Get next command from the queue
            cmd_obj = self._output.get()

            # Send command to the engine
            try:
                self.logger.debug('Sending: {0}'.format(cmd_obj))
                stdout.write('{0}\n'.format(cmd_obj))

                # Flush buffer
                stdout.flush()

            # Interrupt loop on IOError
            except IOError:
                self.logger.debug('Stopping thread')
                break

            # Log exceptions
            except:
                self.logger.exception('Error processing queue')

            # Mark task as done
            finally:
                self._output.task_done()

        self.logger.info('Stopped output')

    def connect(self, role, id=None, type=None):
        """Attach to a socket interface"""

        self.logger.info('Connecting as "{0}"'.format(role))
        self.send(libyate.cmd.Connect(role, id, type))

    def install(self, name, filter_name=None, filter_value=None, priority=None,
                handler=lambda x: x.reply()):
        """Install message handler"""

        self.logger.info('Installing handler for "{0}"'.format(name))

        if name in self.__msg_handlers__:
            raise KeyError('Handler already defined: {0!r}'.format(name))

        self.__msg_handlers__[name] = handler

        self.send(
            libyate.cmd.Install(priority, name, filter_name, filter_value))

    def message(self, name, retvalue=None, kvp=None, id=None, time=None,
                callback=lambda x: None):
        """Send message to the engine"""

        msg = libyate.cmd.Message(id, time, name, retvalue, kvp)
        self.logger.debug('Sending message to the engine: {0!r}'.format(msg))

        if msg.id in self.__msg_callback__:
            raise KeyError('Message ID already in use: {0!r}'.format(msg.id))

        self.__msg_callback__[msg.id] = callback

        self.send(msg)

    def output(self, output):
        """Log message"""

        self.logger.debug('Sending output: {0}'.format(output))
        self.send(libyate.cmd.Output(output))

    def set_local(self, name, value=None):
        """Set or query local parameters"""

        if value:
            self.logger.info('Setting parameter "{0}" to: {1}'
                             .format(name, value))
        else:
            self.logger.info('Querying parameter "{0}"'.format(name))

        self.send(libyate.cmd.SetLocal(name, value))

    def uninstall(self, name):
        """Remove message handler"""

        self.logger.info('Removing handler for "{0}"'.format(name))

        self.__msg_handlers__.pop(name)

        self.send(libyate.cmd.UnInstall(name))

    def unwatch(self, name):
        """Remove message watcher"""

        self.logger.debug('Removing watcher for "{0}"'.format(name))

        self.__msg_watchers__.pop(name)

        self.send(libyate.cmd.UnWatch(name))

    def watch(self, name, handler=lambda x: None):
        """Install message watcher"""

        self.logger.debug('Installing watcher for "{0}"'.format(name))

        if name in self.__msg_watchers__:
            raise KeyError('Watcher already defined: {0!r}'.format(name))

        self.__msg_watchers__[name] = handler

        self.send(libyate.cmd.Watch(name))


class YateSocketClient(YateExtScript):
    """Socket client"""

    # TODO: implement SocketClient class
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError('Socket client not implemented yet')
