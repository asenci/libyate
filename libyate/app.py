"""
libyate - application code
"""

import libyate.cmd
from libyate import cmd_from_string


class YateException(Exception):
    pass


class YateExtScript(object):
    """External script"""

    __msg_handlers__ = {}

    def __init__(self, name=None):
        import logging
        from Queue import Queue

        # Instance name
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

        # Logger instance
        self.logger = logging.getLogger('.'.join([__name__, self.name]))

        # Output queue
        self.output = Queue()

    def run(self, trackparam=True, restart=True):
        """Start processing commands"""
        from sys import stdin
        from threading import Thread

        self.logger.info('Loading module')

        # Initial state
        running = True

        # Output handler thread
        out_handler = Thread(target=self.handle_output, name='OutputHandler')
        out_handler.daemon = True

        # Module startup
        try:
            # Set local parameters
            if trackparam:
                self.set_local('trackparam', self.name)

            if restart is not None:
                self.set_local('restart', restart)

            # Startup hook
            self.logger.debug('Invoking startup hook')
            self.on_start()

        except:
            self.logger.exception('Error during module startup')
            running = False

        else:
            # Start the output handler thread
            self.logger.debug('Starting output handler thread')
            out_handler.start()

        # Main loop
        while running:

            # Process incoming commands
            try:
                line = stdin.readline()

                if line:
                    line = line.rstrip('\n')
                    self.logger.debug('Received: {0}'.format(line))

                    # Start a new handler thread
                    cmd_obj = cmd_from_string(line)
                    Thread(target=self.handle_command, args=(cmd_obj,),
                           name=repr(cmd_obj)).start()

                else:
                    raise EOFError

            except (EOFError, KeyboardInterrupt, SystemExit):
                # Stop the main loop
                running = False

            except:
                # Log exceptions
                self.logger.exception('Error reading from stdin')

        # Module shutdown
        try:
            # Shutdown hook
            self.logger.info('Invoking shutdown hook')
            self.on_stop()

        except:
            self.logger.exception('Error during module shutdown')

        else:
            # Wait for the output queue
            self.logger.debug('Waiting for the output queue')
            self.output.join()

        self.logger.debug('Waiting for all threads to finish processing')

    def on_start(self):
        """Module startup hook"""
        self.logger.debug('Startup hook')

    def on_stop(self):
        """Module shutdown hook"""
        self.logger.debug('Shutdown hook')

    def handle_output(self):
        """Output queue handler"""
        from sys import stdout

        self.logger.info('Started')

        # Main loop
        while True:
            # Get next command from the queue
            cmd_obj = self.output.get()

            try:
                # Send command to the engine
                self.logger.debug('Sending: {0}'.format(cmd_obj))
                stdout.write('{0}\n'.format(cmd_obj))

                # Flush buffer
                stdout.flush()

            # Log exceptions
            except:
                self.logger.exception('Error processing queue')

            finally:
                self.output.task_done()

        self.logger.info('Stopped')

    def handle_command(self, cmd_obj):
        """Command handler"""

        self.logger.debug('Processing command: {0}'.format(cmd_obj))

        try:
            if isinstance(cmd_obj, libyate.cmd.Message):
                handler = self.__msg_handlers__.get(cmd_obj.name)

                if handler:
                    result = handler(cmd_obj)

                    if result is not None:
                        self.output.put(result)

                else:
                    raise YateException('No handler for message: {0}'
                                        .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.Error):
                raise YateException('Invalid command: {0}'
                                    .format(cmd_obj.original))

            elif isinstance(cmd_obj, libyate.cmd.InstallReply):
                if cmd_obj.success:
                    self.logger.debug('Installed handler for {0}'
                                      .format(cmd_obj.name))
                else:
                    self.logger.error('Error installing handler for: {0}'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.SetLocalReply):
                if cmd_obj.success:
                    self.logger.debug('Parameter {0} set to: {1}'
                                      .format(cmd_obj.name, cmd_obj.value))
                else:
                    self.logger.error('Error setting parameter {0}'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.UnInstallReply):
                if cmd_obj.success:
                    self.logger.debug('Removed handler for {0}'
                                      .format(cmd_obj.name))
                else:
                    self.logger.error('Error removing handler for: {0}'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.UnWatchReply):
                if cmd_obj.success:
                    self.logger.debug('Removed watcher for {0}'
                                      .format(cmd_obj.name))
                else:
                    self.logger.error('Error removing watcher for: {0}'
                                      .format(cmd_obj.name))

            elif isinstance(cmd_obj, libyate.cmd.WatchReply):
                if cmd_obj.success:
                    self.logger.debug('Installed watcher for {0}'
                                      .format(cmd_obj.name))
                else:
                    self.logger.error('Error installing watcher for: {0}'
                                      .format(cmd_obj.name))

            else:
                raise YateException('No handler defined for {0}'
                                    .format(type(cmd_obj)))

        except:
            self.logger.exception('Error processing command: {0}'
                                  .format(cmd_obj))

    def connect(self, role, id=None, type=None):
        """Attach to a socket interface"""

        self.logger.debug('Connecting as {0}'.format(role))
        self.output.put(libyate.cmd.Connect(role, id, type))

    def install(self, name, priority=None, filter_name=None, filter_value=None,
                handler=None):
        """Install message handler"""

        self.logger.debug('Installing handler for {0}'.format(name))
        self.__msg_handlers__[name] = handler
        self.output.put(
            libyate.cmd.Install(priority, name, filter_name, filter_value))

    def message(self, name, retvalue=None, kvp=None, id=None, time=None):
        """Send message to the engine"""

        self.output.put(libyate.cmd.Message(id, time, name, retvalue, kvp))

    def output(self, output):
        """Log message"""

        self.output.put(libyate.cmd.Output(output))

    def set_local(self, name, value=None):
        """Set or query local parameters"""

        if value:
            self.logger.debug('Setting parameter {0}: {1}'
                              .format(name, value))
        else:
            self.logger.debug('Querying parameter {0}'.format(name))

        self.output.put(libyate.cmd.SetLocal(name, value))

    def uninstall(self, name):
        """Remove message handler"""

        self.logger.debug('Removing handler for {0}'.format(name))
        self.output.put(libyate.cmd.UnInstall(name))

    def unwatch(self, name):
        """Remove message watcher"""

        self.logger.debug('Removing watcher for {0}'.format(name))
        self.output.put(libyate.cmd.UnWatch(name))

    def watch(self, name, handler=None):
        """Install message watcher"""

        self.logger.debug('Installing watcher for {0}'.format(name))
        self.__msg_handlers__[name] = handler
        self.output.put(libyate.cmd.Watch(name))


class YateSocketClient(YateExtScript):
    """Socket client"""

    # TODO: implement SocketClient class
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError('Socket client not implemented yet')
