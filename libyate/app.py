"""
libyate - application code
"""

import libyate
import libyate.cmd


class YateExtScript(object):
    """Yate external module script"""

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

        # Input queue
        self._input = Queue()

        # Output queue
        self._output = Queue()

    def run(self):
        """User defined startup function"""

    def start(self):
        """Start main loop and wait for commands"""

        self.logger.info('Starting module')

        import signal
        from threading import Thread

        # Register signals
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        if hasattr(signal, 'CTRL_BREAK_EVENT'):
            signal.signal(signal.CTRL_BREAK_EVENT, self.stop)
        if hasattr(signal, 'CTRL_C_EVENT'):
            signal.signal(signal.CTRL_C_EVENT, self.stop)

        # Start the input handler thread
        ti = Thread(target=self.on_input, name='InputThread')
        ti.daemon = True
        ti.start()

        # Start the output handler thread
        to = Thread(target=self.on_output, name='OutputThread')
        to.daemon = True
        to.start()

        # Start the startup handler thread
        ts = Thread(target=self.on_startup, name='StartupThread')
        ts.daemon = True
        ts.start()

        # Main loop
        while True:

            # Process incoming commands
            try:
                cmd = self.receive()

                # Interrupt on None
                if not cmd:
                    break

                # Start a new handler thread
                Thread(target=self.on_command, args=(cmd, ),
                                 name='{0}({1})'.format(
                                     type(cmd).__name__, id(cmd))).start()

            # Log exceptions
            except:
                self.logger.exception('Error processing command')

        self.logger.debug('Waiting for threads')

    def stop(self, signum=None, frame=None):
        self.logger.info('Stopping module')

        # Try to close the input
        try:
            self.close()
        except:
            pass

        # Stop input handler thread
        try:
            self._input.put(None)
        except:
            pass

        # Stop output handler thread
        try:
            self._output.put(None)
        except:
            pass

    def readline(self):
        from sys import stdin

        try:
            string = stdin.readline(8192)

        except ValueError as e:
            raise IOError(str(e))

        if string:
            string = string.rstrip('\n')
            self.logger.debug('Received {0} bytes: {1}'
                              .format(len(string.encode()), string))
            return string

        else:
            raise EOFError('Received EOF')

    def write(self, string):
        from sys import stdout

        self.logger.debug('Sending {0} bytes: {1}'
                          .format(len(string.encode()), string))

        try:
            stdout.write(string + '\n')

        except ValueError as e:
            raise IOError(str(e))

        else:
            # Flush buffer
            stdout.flush()

    def close(self):
        from sys import stdin
        stdin.close()

    def receive(self):
        from Queue import Empty

        while True:
            try:
                string = self._input.get(timeout=10)
                self._input.task_done()

                if string is not None:
                    return libyate.cmd_from_string(string)

                break

            except Empty:
                continue

    def send(self, command):
        self._output.put(str(command))

    def on_input(self):
        """Input handler"""

        self.logger.debug('Started input')

        # Main loop
        while True:

            try:
                self._input.put(self.readline())

            # Interrupt on EOFError
            except EOFError:
                self.logger.debug('Stopping input')
                break

            # Interrupt on IOError
            except IOError:
                self.logger.exception('Stopping input')
                break

            # Log exceptions
            except:
                self.logger.exception('Error processing input')

        # Stop module
        self.stop()

    def on_output(self):
        """Output handler"""

        from Queue import Empty

        self.logger.debug('Started output')

        # Main loop
        while True:

            # Send string to the engine
            try:

                # Get next string from the queue
                string = self._output.get(timeout=10)
                self._output.task_done()

                if string is None:
                    break

                self.write(string)

            except Empty:
                continue

            # Interrupt on IOError
            except IOError:
                self.logger.exception('Stopping output')
                break

            # Log exceptions
            except:
                self.logger.exception('Error processing output')

        # Stop module
        self.stop()

    def on_startup(self):
        try:
            # Execute user code
            self.logger.debug('Executing user code')
            self.run()

        except:
            self.logger.exception('Error on module startup')
            self.stop()

    def on_command(self, cmd):
        """Command handler"""

        self.logger.debug('Received command: {0!r}'.format(cmd))

        try:
            if isinstance(cmd, (libyate.cmd.Message,
                                libyate.cmd.MessageReply)):

                # Message from installed handlers
                if isinstance(cmd, libyate.cmd.Message):
                    handler = self.__msg_handlers__[cmd.name]

                # Reply from application generated message
                elif cmd.id is not None:
                    handler = self.__msg_callback__.pop(cmd.id).callback

                # Notification from installed watchers
                else:
                    handler = self.__msg_watchers__[cmd.name]

                self.logger.debug('Handler: {0}'.format(handler))
                result = handler(cmd)

                self.logger.debug('Result: {0}'.format(result))
                if result is not None:
                    self.send(result)

            elif isinstance(cmd, libyate.cmd.Error):
                self.logger.error('Invalid command: {0}'
                                  .format(cmd.original))

            elif isinstance(cmd, libyate.cmd.InstallReply):
                if cmd.success:
                    self.logger.info('Installed handler for "{0}"'
                                     .format(cmd.name))
                else:
                    self.logger.error('Error installing handler for "{0}"'
                                      .format(cmd.name))

            elif isinstance(cmd, libyate.cmd.SetLocalReply):
                if cmd.success:
                    self.logger.info('Parameter "{0}" set to: {1}'
                                     .format(cmd.name, cmd.value))
                else:
                    self.logger.error('Error setting parameter "{0}"'
                                      .format(cmd.name))

            elif isinstance(cmd, libyate.cmd.UnInstallReply):
                if cmd.success:
                    self.logger.info('Removed handler for "{0}"'
                                     .format(cmd.name))
                else:
                    self.logger.error('Error removing handler for "{0}"'
                                      .format(cmd.name))

            elif isinstance(cmd, libyate.cmd.UnWatchReply):
                if cmd.success:
                    self.logger.info('Removed watcher for "{0}"'
                                     .format(cmd.name))
                else:
                    self.logger.error('Error removing watcher for "{0}"'
                                      .format(cmd.name))

            elif isinstance(cmd, libyate.cmd.WatchReply):
                if cmd.success:
                    self.logger.info('Installed watcher for "{0}"'
                                     .format(cmd.name))
                else:
                    self.logger.error('Error installing watcher for "{0}"'
                                      .format(cmd.name))

            else:
                self.logger.critical('No handler defined for "{0}" command'
                                     .format(type(cmd).__name__))

        except:
            self.logger.exception('Error processing command: {0}'
                                  .format(cmd))

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
        msg.callback = callback

        self.logger.debug('Sending message to the engine: {0!r}'.format(msg))

        if msg.id in self.__msg_callback__:
            raise KeyError('Message ID already in use: {0!r}'.format(msg.id))

        self.__msg_callback__[msg.id] = msg

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


class YateExtClient(YateExtScript):
    """Yate external module socket client"""

    def __init__(self, host_or_path, port=None, name=None):
        super(YateExtClient, self).__init__(name)

        self._host_or_path = host_or_path
        self._port = port

        self._socket = None
        self._recv_buff = None

    def start(self):

        # Try to connect the socket
        try:

            # UNIX socket
            if self._host_or_path[0] in ['.', '/']:
                from socket import socket
                from socket import AF_UNIX, SOCK_STREAM

                self._socket = socket(family=AF_UNIX)
                self._socket.connect(self._host_or_path)

            # INET/INET6 socket
            else:
                from socket import socket, getaddrinfo, error
                from socket import AF_UNSPEC, SOCK_STREAM, IPPROTO_TCP

                # Get protocols and addresses
                l = getaddrinfo(self._host_or_path, self._port, AF_UNSPEC,
                                SOCK_STREAM, IPPROTO_TCP)

                while l:

                    # Get connection data
                    f, t, p, c, a = l.pop()

                    # Try to create the socket
                    try:
                        self._socket = socket(f, t, p)

                    # Error creating the socket
                    except error:

                        # Try next resource
                        if l:
                            continue

                        # No resources left
                        raise

                    # Try to connect to the address
                    try:
                        self._socket.connect(a)

                    # Error connecting to the address
                    except error:
                        self._socket.close()

                        # Try next resource
                        if l:
                            continue

                        # No resources left
                        raise

                    # Socket connected, continue execution
                    break

        # Failed to connect the socket
        except:
            self.logger.exception('Failed to connect')

        # Socket connected, continue startup
        else:

            # Clean receive buffer
            self._recv_buff = ''

            # Main loop
            super(YateExtClient, self).start()

            # Close socket
            self._socket.close()

    def readline(self):
        from socket import error

        # Continue receiving until '\n' is received
        while '\n' not in self._recv_buff:

            try:
                data = self._socket.recv(8192)
            except error as e:
                raise IOError(str(e))

            # Append received data to the buffer
            if data:
                self._recv_buff += data

            # No data received (socket has been closed)
            else:
                raise EOFError('Socket closed')

        # Get the received command and leave any additional data on the buffer
        string, self._recv_buff = self._recv_buff.partition('\n')[::2]

        self.logger.debug('Received {0} bytes: {1}'
                          .format(len(string.encode()), string))
        return string

    def write(self, string):
        from socket import error

        self.logger.debug('Sending {0} bytes: {1}'
                          .format(len(string.encode()), string))

        try:
            self._socket.sendall(string + '\n')

        except error as e:
            raise IOError(str(e))

    def close(self):
        from socket import error, SHUT_RD

        # Close socket for read operations
        self._socket.shutdown(SHUT_RD)
