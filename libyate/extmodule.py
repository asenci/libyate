"""
libyate - external module application code
"""

import logging
import Queue
import signal
import socket
import sys

from abc import ABCMeta, abstractmethod
from threading import Thread

import libyate.engine


# noinspection PyBroadException
class Application(object):
    """Yate external module application

    :param str name: application name for logging purposes
    :param str trackparam: value for handler tracking parameter
    :param bool restart: restart module if it terminates unexpectedly
    """

    __metaclass__ = ABCMeta

    def __init__(self, name=None, trackparam=None, restart=None):

        self.__msg_callback__ = {}
        self.__msg_handlers__ = {}
        self.__msg_watchers__ = {}

        self.__input_buffer__ = None

        self.__input_queue__ = Queue.Queue()
        self.__output_queue__ = Queue.Queue()
        self.__startup_queue__ = Queue.Queue()

        if name is None:
            self.logger = logging.getLogger(
                '.'.join((self.__module__, self.__class__.__name__)))

        else:
            self.logger = logging.getLogger(name)

        if trackparam is not None:
            self.logger.debug('Setting handler tracking parameter')
            self.set_local('trackparam', trackparam)

        if restart is not None:
            self.logger.debug('Setting module restart parameter')
            self.set_local('restart', 'true' if restart else 'false')

    @abstractmethod
    def readline(self):
        """Get the next command from the engine

        :return: Command string
        :rtype: str
        :raise EOFError: on input exhaustion
        :raise IOError: on Input/Output errors
        """

        pass

    @abstractmethod
    def write(self, string):
        """Send command to the engine

        :param str string: Command string to be sent
        :raise IOError: on Input/Output errors
        """

        pass

    @abstractmethod
    def close(self):
        """Close input and stop receiving commands"""

        pass

    def main(self, threaded=True):
        """Module main loop

        :param bool threaded: each message will be processed on it's own thread
        """

        self.__input_buffer__ = ''

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        if hasattr(signal, 'CTRL_BREAK_EVENT'):
            signal.signal(signal.CTRL_BREAK_EVENT, self.stop)
        if hasattr(signal, 'CTRL_C_EVENT'):
            signal.signal(signal.CTRL_C_EVENT, self.stop)

        self.logger.info('Starting module threads')

        ti = Thread(target=self._input, name='InputThread')
        ti.daemon = True
        ti.start()

        to = Thread(target=self._output, name='OutputThread')
        to.daemon = True
        to.start()

        tm = Thread(target=self._main, name='MainLoopThread',
                    kwargs={'threaded': threaded})
        tm.daemon = True
        tm.start()

        startup_queue, self.__startup_queue__ = self.__startup_queue__, None

        self.logger.debug('Dumping the startup queue into the output queue')
        while not startup_queue.empty():
            self.__output_queue__.put(startup_queue.get())

        self.logger.debug('Executing user startup code')
        try:
            self.start()

        except:
            self.logger.exception('Error executing user startup code')
            raise

        self.logger.debug('Entering main loop')
        while True:
            tm.join(60)
            if not tm.is_alive():
                break

        self.logger.debug('Waiting for threads')

    def start(self):
        """Module startup routine"""
        pass

    # noinspection PyUnusedLocal
    def stop(self, signum=None, frame=None):
        """Module shutdown routine

        :param signum: signal number
        :param frame: current stack frame
        """
        self.logger.info('Stopping module')

        try:
            self.close()
        except:
            pass

        try:
            self.__input_queue__.put(None)
        except:
            pass

        try:
            self.__output_queue__.put(None)
        except:
            pass

    def _command(self, cmd):
        """Handler function for command handling threads

        :param libyate.engine.Command cmd: A libyate Command object to process
        """

        self.logger.debug('Received command: {0!r}'.format(cmd))

        handler = {
            libyate.engine.Error: self._command_error,
            libyate.engine.InstallReply: self._command_install_reply,
            libyate.engine.Message: self._command_message,
            libyate.engine.MessageReply: self._command_message,
            libyate.engine.SetLocalReply: self._command_setlocal_reply,
            libyate.engine.UnInstallReply: self._command_uninstall_reply,
            libyate.engine.UnWatchReply: self._command_unwatch_reply,
            libyate.engine.WatchReply: self._command_watch_reply,
        }.get(type(cmd))

        if handler is None:
            self.logger.critical('No handler defined for "{0}" command'
                                 .format(type(cmd).__name__))

        try:
            handler(cmd)
        except:
            self.logger.exception('Error processing command: {0}'
                                  .format(cmd))

    def _command_error(self, cmd):
        """Handler function for Error commands

        :param libyate.cmd.Error cmd: A libyate Error object to process
        """

        try:
            orig_cmd = libyate.engine.from_string(cmd.original)
        except:
            pass
        else:
            if isinstance(orig_cmd, libyate.engine.Message):
                if self.__msg_callback__.pop(orig_cmd.id) is not None:
                    raise RuntimeError('Error processing message: {0!r}'
                                       .format(orig_cmd))

        self.logger.error('Invalid command: {0}'.format(cmd.original))

    def _command_install_reply(self, cmd):
        """Handler function for InstallReply commands

        :param libyate.cmd.InstallReply cmd: A libyate InstallReply object to
            process
        """

        if cmd.success:
            self.logger.info('Installed handler for "{0}"'
                             .format(cmd.name))
        else:
            self.logger.error('Error installing handler for "{0}"'
                              .format(cmd.name))

    def _command_message(self, cmd):
        """Handler function for Message and MessageReply commands

        :param cmd: A libyate Message or MessageReply object to process
        :type cmd: libyate.cmd.Message or libyate.cmd.MessageReply
        """

        try:
            # Message from installed handlers
            if isinstance(cmd, libyate.engine.Message):
                handler = self.__msg_handlers__[cmd.name]

            # Reply from application generated message
            elif cmd.id is not None:
                handler = self.__msg_callback__.pop(cmd.id)

            # Notification from installed watchers
            else:
                handler = self.__msg_watchers__[cmd.name]

            self.logger.debug('Handler: {0}'.format(handler))

            if handler is not None:
                result = handler(cmd)

                self.logger.debug('Result: {0}'.format(result))

                if result is not None:
                    self._send(result)

        except:
            self.logger.exception('Error processing message: {0}'.format(cmd))
            if isinstance(cmd, libyate.engine.Message):
                self._send(cmd.reply())

    def _command_setlocal_reply(self, cmd):
        """Handler function for SetLocalReply commands

        :param libyate.cmd.SetLocalReply cmd: A libyate SetLocalReply object to
            process
        """

        if cmd.success:
            self.logger.info('Parameter "{0}" set to: {1}'
                             .format(cmd.name, cmd.value))
        else:
            self.logger.error('Error setting parameter "{0}"'
                              .format(cmd.name))

    def _command_uninstall_reply(self, cmd):
        """Handler function for UninstallReply commands

        :param libyate.cmd.UninstallReply cmd: A libyate UninstallReply object
            to process
        """

        if cmd.success:
            self.logger.info('Removed handler for "{0}"'
                             .format(cmd.name))
        else:
            self.logger.error('Error removing handler for "{0}"'
                              .format(cmd.name))

    def _command_unwatch_reply(self, cmd):
        """Handler function for UnwatchReply commands

        :param libyate.cmd.UnwatchReply cmd: A libyate UnwatchReply object to
            process
        """

        if cmd.success:
            self.logger.info('Removed watcher for "{0}"'
                             .format(cmd.name))
        else:
            self.logger.error('Error removing watcher for "{0}"'
                              .format(cmd.name))

    def _command_watch_reply(self, cmd):
        """Handler function for WatchReply commands

        :param libyate.cmd.WatchReply cmd: A libyate WatchReply object to
            process
        """

        if cmd.success:
            self.logger.info('Installed watcher for "{0}"'
                             .format(cmd.name))
        else:
            self.logger.error('Error installing watcher for "{0}"'
                              .format(cmd.name))

    def _input(self):
        """Handler function for the input handling thread"""

        self.logger.debug('Started input')

        while True:

            try:
                self.__input_queue__.put(self.readline())

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

        # Shutdown module if the input handling thread stops
        self.stop()

    def _main(self, threaded=True):
        """Handler function for the main loop thread"""

        self.logger.debug('Started main loop')

        while True:

            try:
                cmd = self._receive()

                if not cmd:
                    break

                if threaded:
                    Thread(target=self._command, args=(cmd, ),
                           name='{0}({1})'.format(
                               type(cmd).__name__, id(cmd))).start()

                else:
                    self._command(cmd)

            except:
                self.logger.exception('Error processing command')

    def _output(self):
        """Handler function for the output handling thread"""

        self.logger.debug('Started output')

        while True:

            try:
                string = self.__output_queue__.get(timeout=10)
                self.__output_queue__.task_done()

                if string is None:
                    break

                self.write(string)

            except Queue.Empty:
                # Loop until an item is available on the queue,
                # the thread will not receive system signals if a timeout is
                #   not specified
                continue

            # Interrupt on IOError
            except IOError:
                self.logger.exception('Stopping output')
                break

            # Log exceptions
            except:
                self.logger.exception('Error processing output')

        # Shutdown module if the output handling thread stops
        self.stop()

    def _receive(self):
        """Get the next command object from the input queue

        :return: A command object
        :rtype: libyate.cmd.Command
        """

        # Loop until an item is available on the queue, the thread will not
        #   receive system signals if a timeout is not specified

        while True:
            try:
                string = self.__input_queue__.get(timeout=10)
                self.__input_queue__.task_done()

                if string is not None:
                    return libyate.engine.from_string(string)

                break

            except Queue.Empty:
                continue

    def _send(self, command, force=False):
        """Insert command into the output queue

        :param libyate.cmd.Command command: a libyate Command object to send
            to the engine
        :param bool force: force sending to the output queue even if the main
            thread is not yet started
        """

        if force or self.__startup_queue__ is None:
            queue = self.__output_queue__
        else:
            queue = self.__startup_queue__

        queue.put('{0}\n'.format(command))

    # noinspection PyShadowingBuiltins
    def connect(self, role, id=None, type=None):
        """Attach to a socket interface

        :param str role: role of this connection: global, channel, play,
            record, playrec
        :param str id: channel id to connect this socket to
        :param str type: type of data channel, assuming audio if missing
        """

        self.logger.info('Connecting as "{0}"'.format(role))
        self._send(libyate.engine.Connect(role, id, type), force=True)

    def install(self, handler, name, priority=None, filter_name=None,
                filter_value=None):
        """Install message handler

        :param function handler: handler function for received messages
        :param str name: name of the messages for that a handler should be
            installed
        :param priority: priority in chain, default 100 if missing
        :type priority: str or int
        :param str filter_name: name of a variable the handler will filter
        :param str filter_value: matching value for the filtered variable
        """

        self.logger.info('Installing handler for "{0}"'.format(name))

        if name in self.__msg_handlers__:
            raise KeyError('Handler already defined: {0!r}'.format(name))

        self.__msg_handlers__[name] = handler

        self._send(
            libyate.engine.Install(priority, name, filter_name, filter_value))

    # noinspection PyShadowingBuiltins
    def message(self, name, kvp=None, id=None, time=None, retvalue=None,
                callback=None):
        """Send message to the engine

        :param str name: name of the message
        :param kvp: enumeration of the key-value pairs of the message
        :type kvp: dict, list, set, tuple or libyate.type.OrderedDict
        :param str id: obscure unique message ID string generated by Yate
        :param time: time (in seconds) the message was initially created
        :type time: str, int or datetime.datetime
        :param str retvalue: default textual return value of the message
        :param function callback: handler function for message reply
        """

        msg = libyate.engine.Message(id, time, name, retvalue, kvp)

        self.logger.debug('Sending message to the engine: {0!r}'.format(msg))

        if msg.id in self.__msg_callback__:
            raise KeyError('Message ID already in use: {0}'.format(msg.id))

        self.__msg_callback__[msg.id] = callback

        self._send(msg)

    def output(self, output):
        """Send messages to the engine logging output

        :param str output: arbitrary unescaped string
        """

        self.logger.debug('Sending output: {0}'.format(output))
        self._send(libyate.engine.Output(output))

    def set_local(self, name, value=None):
        """Set or query local parameters

        :param str name: name of the parameter to modify
        :param value: new value to set in the local module instance, empty to
            just query
        :type value: str, int or bool
        """

        if value:
            self.logger.info('Setting parameter "{0}" to: {1}'
                             .format(name, value))
        else:
            self.logger.info('Querying parameter "{0}"'.format(name))

        self._send(libyate.engine.SetLocal(name, value))

    def uninstall(self, name):
        """Remove message handler

        :param str name: name of the message handler that should be uninstalled
        """

        self.logger.info('Removing handler for "{0}"'.format(name))

        self.__msg_handlers__.pop(name)

        self._send(libyate.engine.UnInstall(name))

    def unwatch(self, name):
        """Remove message watcher

        :param str name: name of the message watcher that should be uninstalled
        """

        self.logger.debug('Removing watcher for "{0}"'.format(name))

        self.__msg_watchers__.pop(name)

        self._send(libyate.engine.UnWatch(name))

    def watch(self, handler, name):
        """Install message watcher

        :param function handler: handler function for received notifications
        :param str name: name of the messages for that a watcher should be
            installed
        """

        self.logger.debug('Installing watcher for "{0}"'.format(name))

        if name in self.__msg_watchers__:
            raise KeyError('Watcher already defined: {0!r}'.format(name))

        self.__msg_watchers__[name] = handler

        self._send(libyate.engine.Watch(name))


# noinspection PyBroadException
class Script(Application):
    """Yate external module script"""

    def readline(self):
        """Get the next command from the engine

        :return: Command string
        :rtype: str
        :raise EOFError: on input exhaustion
        :raise IOError: on input/output errors
        """

        while '\n' not in self.__input_buffer__:

            try:
                data = sys.stdin.readline(8192)
            except ValueError as e:
                raise IOError(str(e))

            if data == '':
                raise EOFError('Received EOF')

            self.logger.debug('Received {0} bytes: {1!r}'
                              .format(len(data), data))

            self.__input_buffer__ += data

        line, self.__input_buffer__ = \
            self.__input_buffer__.partition('\n')[::2]

        return line

    def write(self, string):
        """Send command to the engine

        :param str string: Command string to be sent
        :raise IOError: on input/output errors
        """

        self.logger.debug('Sending {0} bytes: {1!r}'
                          .format(len(string), string))

        try:
            sys.stdout.write(string)

        except ValueError as e:
            raise IOError(str(e))

        else:
            sys.stdout.flush()

    def close(self):
        """Close input and stop receiving commands"""

        sys.stdin.close()


# noinspection PyBroadException
class SocketClient(Application):
    """Yate external module socket client

    :param str role: role of this connection: global, channel, play,
        record, playrec
    :param str host_or_path: Yate listener host address or path to the Yate
        listener unix socket
    :param int port: Yate listener port number
    :param str name: Application name for logging purposes
    :param str trackparam: value for handler tracking parameter
    :param bool restart: restart module if it terminates unexpectedly
    :param str id: channel id to connect this socket to
    :param str type: type of data channel, assuming audio if missing
    """

    def __init__(self, role, host_or_path, port=None, name=None, trackparam=None,
                 restart=None, id=None, type=None):

        super(SocketClient, self).__init__(
            name=name, trackparam=trackparam, restart=restart)

        self.connect(role=role, id=id, type=type)

        if host_or_path is None:
            raise ValueError('Either a host or a path must be specified')
        if host_or_path[0] not in ['.', '/'] and port is None:
            raise ValueError('Port number must be specified for tcp hosts')

        # Try to connect the socket
        try:

            # UNIX socket
            if host_or_path[0] in ['.', '/']:
                self.__socket__ = socket.socket(family=socket.AF_UNIX)
                self.__socket__.connect(host_or_path)

            # INET/INET6 socket
            else:
                # Get protocols and addresses
                l = socket.getaddrinfo(host_or_path, port, socket.AF_UNSPEC,
                                       socket.SOCK_STREAM, socket.IPPROTO_TCP)

                while l:

                    # Get connection data
                    f, t, p, c, a = l.pop()

                    # Try to create the socket
                    try:
                        self.__socket__ = socket.socket(f, t, p)

                    # Error creating the socket
                    except socket.error:

                        # Try next resource
                        if l:
                            continue

                        # No resources left
                        raise

                    # Try to connect to the address
                    try:
                        self.__socket__.connect(a)

                    # Error connecting to the address
                    except socket.error:
                        self.__socket__.close()

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

    def __del__(self):
        if self.__socket__ is not None:
            self.__socket__.close()
            self.__socket__ = None

    def readline(self):
        """Get the next command from the engine

        :return: Command string
        :rtype: str
        :raise EOFError: on input exhaustion
        :raise IOError: on input/output errors
        """

        # Continue receiving until '\n' is received
        while '\n' not in self.__input_buffer__:

            try:
                data = self.__socket__.recv(8192)
            except socket.error as e:
                raise IOError(str(e))

            if data == '':
                raise EOFError('Socket closed')

            self.logger.debug('Received {0} bytes: {1!r}'
                              .format(len(data), data))

            self.__input_buffer__ += data

        line, self.__input_buffer__ = \
            self.__input_buffer__.partition('\n')[::2]

        return line

    def write(self, string):
        """Send command to the engine

        :param str string: Command string to be sent
        :raise IOError: on input/output errors
        """

        self.logger.debug('Sending {0} bytes: {1!r}'
                          .format(len(string), string))

        try:
            self.__socket__.sendall(string)

        except socket.error as e:
            raise IOError(str(e))

    def close(self):
        """Close input and stop receiving commands"""

        if self.__socket__ is not None:

            try:
                # Close socket for read operations
                self.__socket__.shutdown(socket.SHUT_RD)

            except socket.error:
                pass
