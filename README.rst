=======
libyate
=======

Python library for developing Yate external applications


Sample script application:
--------------------------

* extmodule.conf

.. sourcecode:: cfg

    [scripts]
    sample.py=-d


* sample.py

.. sourcecode:: python

    #!/usr/bin/env python
    """
    Sample application to test libyate
    """

    import libyate.app


    class MyApp(libyate.app.Script):
        def run(self):
            # Query engine version
            self.set_local('engine.version')

            # Install handler for "call.route"
            self.install('call.route', priority=50, handler=self.call_route)

            # Install watcher for "engine.timer"
            self.watch('engine.timer', handler=self.timer)

            # Send a message to the engine
            self.message(name='myapp.test', id='somerandomid',
                         kvp={'testing': True,
                              'done': '75%',
                              'path': '/bin:/usr/bin'},
                         callback=self.reply)

            from time import sleep
            sleep(1)
            self.unwatch('engine.timer')

        def call_route(self, msg):
            self.logger.info('Handling "call.route": {0!r}'.format(msg))

            # Just reply with processed = False
            return msg.reply()

        def reply(self, msg):
            self.logger.info('Got reply for "{0}"'.format(msg.id))

        def timer(self, msg):
            self.logger.info('Some periodic routine')


    if __name__ == '__main__':

        import logging
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('-d', '--debug', action='store_true', default=False,
                          help='increase logging verbosity')
        parser.add_option('-q', '--quiet', action='store_true', default=False,
                          help='reduce the logging verbosity')
        options, _ = parser.parse_args()

        log_format = \
            '%(asctime)s <%(name)s[%(threadName)s]:%(levelname)s> %(message)s'

        logging.basicConfig(**{
            'level': (logging.DEBUG if options.debug else
                      logging.WARN if options.quiet else
                      logging.INFO),
            'format': log_format,
        })

        MyApp('sample.py').start()


* Output:

::

    2014-07-01 10:37:05,753 <sample.py[MainThread]:INFO> Starting module
    2014-07-01 10:37:05,753 <sample.py[InputThread]:DEBUG> Started input
    2014-07-01 10:37:05,754 <sample.py[OutputThread]:DEBUG> Started output
    2014-07-01 10:37:05,754 <sample.py[StartupThread]:DEBUG> Executing user code
    2014-07-01 10:37:05,754 <sample.py[StartupThread]:INFO> Querying parameter "engine.version"
    2014-07-01 10:37:05,755 <sample.py[StartupThread]:INFO> Installing handler for "call.route"
    2014-07-01 10:37:05,755 <sample.py[StartupThread]:DEBUG> Installing watcher for "engine.timer"
    2014-07-01 10:37:05,757 <sample.py[StartupThread]:DEBUG> Sending message to the engine: libyate.cmd.Message('somerandomid', datetime.datetime(2014, 7, 1, 13, 37, 5, 755787), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2014-07-01 10:37:05,758 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: %%>setlocal:engine.version:
    2014-07-01 10:37:05,759 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: %%>install:50:call.route::
    2014-07-01 10:37:05,759 <sample.py[OutputThread]:DEBUG> Sending 21 bytes: %%>watch:engine.timer
    2014-07-01 10:37:05,759 <sample.py[OutputThread]:DEBUG> Sending 89 bytes: %%>message:somerandomid:1404221825:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-07-01 10:37:05,763 <sample.py[InputThread]:DEBUG> Received 37 bytes: %%<setlocal:engine.version:5.3.0:true
    2014-07-01 10:37:05,763 <sample.py[InputThread]:DEBUG> Received 29 bytes: %%<install:50:call.route:true
    2014-07-01 10:37:05,763 <sample.py[InputThread]:DEBUG> Received 26 bytes: %%<watch:engine.timer:true
    2014-07-01 10:37:05,766 <sample.py[SetLocalReply(4473274896)]:DEBUG> Received command: libyate.cmd.SetLocalReply('engine.version', '5.3.0', True)
    2014-07-01 10:37:05,766 <sample.py[InstallReply(4473277072)]:DEBUG> Received command: libyate.cmd.InstallReply(50, 'call.route', True)
    2014-07-01 10:37:05,767 <sample.py[SetLocalReply(4473274896)]:INFO> Parameter "engine.version" set to: 5.3.0
    2014-07-01 10:37:05,767 <sample.py[InstallReply(4473277072)]:INFO> Installed handler for "call.route"
    2014-07-01 10:37:05,767 <sample.py[WatchReply(4473277776)]:DEBUG> Received command: libyate.cmd.WatchReply('engine.timer', True)
    2014-07-01 10:37:05,768 <sample.py[WatchReply(4473277776)]:INFO> Installed watcher for "engine.timer"
    2014-07-01 10:37:05,769 <sample.py[InputThread]:DEBUG> Received 84 bytes: %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-07-01 10:37:05,769 <sample.py[MessageReply(4471455056)]:DEBUG> Received command: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-07-01 10:37:05,769 <sample.py[MessageReply(4471455056)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x10a9fddd0>>
    2014-07-01 10:37:05,770 <sample.py[MessageReply(4471455056)]:INFO> Got reply for "somerandomid"
    2014-07-01 10:37:05,770 <sample.py[MessageReply(4471455056)]:DEBUG> Result: None
    2014-07-01 10:37:06,004 <sample.py[InputThread]:DEBUG> Received 115 bytes: %%<message::false:engine.timer::time=1404221826:nodename=localhost:handlers=tone%z90,sip%z90,yrtp%z90,regfile%z100
    2014-07-01 10:37:06,040 <sample.py[MessageReply(4473277904)]:DEBUG> Received command: libyate.cmd.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1404221826'), ('nodename', 'localhost'), ('handlers', 'tone:90,sip:90,yrtp:90,regfile:100'))))
    2014-07-01 10:37:06,040 <sample.py[MessageReply(4473277904)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x10a9fddd0>>
    2014-07-01 10:37:06,040 <sample.py[MessageReply(4473277904)]:INFO> Some periodic routine
    2014-07-01 10:37:06,040 <sample.py[MessageReply(4473277904)]:DEBUG> Result: None
    2014-07-01 10:37:06,760 <sample.py[StartupThread]:DEBUG> Removing watcher for "engine.timer"
    2014-07-01 10:37:06,793 <sample.py[OutputThread]:DEBUG> Sending 23 bytes: %%>unwatch:engine.timer
    2014-07-01 10:37:06,798 <sample.py[InputThread]:DEBUG> Received 28 bytes: %%<unwatch:engine.timer:true
    2014-07-01 10:37:06,818 <sample.py[UnWatchReply(4471455056)]:DEBUG> Received command: libyate.cmd.UnWatchReply('engine.timer', True)
    2014-07-01 10:37:06,818 <sample.py[UnWatchReply(4471455056)]:INFO> Removed watcher for "engine.timer"
    ^CYate engine is shutting down with code 0
    2014-07-01 10:37:12,643 <sample.py[MainThread]:INFO> Stopping module
    2014-07-01 10:37:12,644 <sample.py[MainThread]:DEBUG> Waiting for threads


Sample socket client application:
---------------------------------

* extmodule.conf

.. sourcecode:: cfg

    [listener sample]
    type=unix
    path=/tmp/sample.sock


* sample.py

.. sourcecode:: python

    #!/usr/bin/env python
    """
    Sample application to test libyate
    """

    import libyate.app


    class MyApp(libyate.app.SocketClient):
        def run(self):
            # Connect to the engine
            self.connect('global')

            # Send message to the engine
            self.output('Starting sample.py')

            # Query engine version
            self.set_local('engine.version')

            # Install handler for "call.route"
            self.install('call.route', priority=50, handler=self.call_route)

            # Install watcher for "engine.timer"
            self.watch('engine.timer', handler=self.timer)

            # Send a message to the engine
            self.message(name='myapp.test', id='somerandomid',
                         kvp={'testing': True,
                              'done': '75%',
                              'path': '/bin:/usr/bin'},
                         callback=self.reply)

            from time import sleep
            sleep(1)
            self.unwatch('engine.timer')

        def call_route(self, msg):
            self.logger.info('Handling "call.route": {0!r}'.format(msg))

            # Just reply with processed = False
            return msg.reply()

        def reply(self, msg):
            self.logger.info('Got reply for "{0}"'.format(msg.id))

        def timer(self, msg):
            self.logger.info('Some periodic routine')


    if __name__ == '__main__':

        import logging
        from optparse import OptionParser

        parser = OptionParser('usage: %prog [options] <host or path> [port]')
        parser.add_option('-d', '--debug', action='store_true', default=False,
                          help='increase logging verbosity')
        parser.add_option('-q', '--quiet', action='store_true', default=False,
                          help='reduce the logging verbosity')

        options, args = parser.parse_args()

        if len(args) < 1:
            parser.error('either a host or a path must be specified')

        log_format = \
            '%(asctime)s <%(name)s[%(threadName)s]:%(levelname)s> %(message)s'

        logging.basicConfig(**{
            'level': (logging.DEBUG if options.debug else
                      logging.WARN if options.quiet else
                      logging.INFO),
            'format': log_format,
        })

        MyApp(*args, name='sample.py').start()


* Expected output:

::

    $ sample.py -d /tmp/sample.sock
    2014-07-01 10:38:33,722 <sample.py[MainThread]:INFO> Starting module
    2014-07-01 10:38:33,723 <sample.py[InputThread]:DEBUG> Started input
    2014-07-01 10:38:33,723 <sample.py[OutputThread]:DEBUG> Started output
    2014-07-01 10:38:33,724 <sample.py[StartupThread]:DEBUG> Executing user code
    2014-07-01 10:38:33,724 <sample.py[StartupThread]:INFO> Connecting as "global"
    2014-07-01 10:38:33,725 <sample.py[StartupThread]:DEBUG> Sending output: Starting sample.py
    2014-07-01 10:38:33,725 <sample.py[StartupThread]:INFO> Querying parameter "engine.version"
    2014-07-01 10:38:33,726 <sample.py[StartupThread]:INFO> Installing handler for "call.route"
    2014-07-01 10:38:33,726 <sample.py[StartupThread]:DEBUG> Installing watcher for "engine.timer"
    2014-07-01 10:38:33,727 <sample.py[StartupThread]:DEBUG> Sending message to the engine: libyate.cmd.Message('somerandomid', datetime.datetime(2014, 7, 1, 13, 38, 33, 726707), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2014-07-01 10:38:33,728 <sample.py[OutputThread]:DEBUG> Sending 19 bytes: %%>connect:global::
    2014-07-01 10:38:33,729 <sample.py[OutputThread]:DEBUG> Sending 28 bytes: %%>output:Starting sample.py
    2014-07-01 10:38:33,729 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: %%>setlocal:engine.version:
    2014-07-01 10:38:33,729 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: %%>install:50:call.route::
    2014-07-01 10:38:33,729 <sample.py[OutputThread]:DEBUG> Sending 21 bytes: %%>watch:engine.timer
    2014-07-01 10:38:33,729 <sample.py[OutputThread]:DEBUG> Sending 89 bytes: %%>message:somerandomid:1404221913:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-07-01 10:38:33,734 <sample.py[InputThread]:DEBUG> Received 37 bytes: %%<setlocal:engine.version:5.3.0:true
    2014-07-01 10:38:33,734 <sample.py[InputThread]:DEBUG> Received 29 bytes: %%<install:50:call.route:true
    2014-07-01 10:38:33,735 <sample.py[InputThread]:DEBUG> Received 26 bytes: %%<watch:engine.timer:true
    2014-07-01 10:38:33,740 <sample.py[InputThread]:DEBUG> Received 84 bytes: %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-07-01 10:38:33,743 <sample.py[SetLocalReply(4462266064)]:DEBUG> Received command: libyate.cmd.SetLocalReply('engine.version', '5.3.0', True)
    2014-07-01 10:38:33,743 <sample.py[SetLocalReply(4462266064)]:INFO> Parameter "engine.version" set to: 5.3.0
    2014-07-01 10:38:33,744 <sample.py[InstallReply(4460445008)]:DEBUG> Received command: libyate.cmd.InstallReply(50, 'call.route', True)
    2014-07-01 10:38:33,744 <sample.py[InstallReply(4460445008)]:INFO> Installed handler for "call.route"
    2014-07-01 10:38:33,744 <sample.py[WatchReply(4462267408)]:DEBUG> Received command: libyate.cmd.WatchReply('engine.timer', True)
    2014-07-01 10:38:33,745 <sample.py[WatchReply(4462267408)]:INFO> Installed watcher for "engine.timer"
    2014-07-01 10:38:33,746 <sample.py[MessageReply(4462266640)]:DEBUG> Received command: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-07-01 10:38:33,746 <sample.py[MessageReply(4462266640)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x109f7af50>>
    2014-07-01 10:38:33,746 <sample.py[MessageReply(4462266640)]:INFO> Got reply for "somerandomid"
    2014-07-01 10:38:33,746 <sample.py[MessageReply(4462266640)]:DEBUG> Result: None
    2014-07-01 10:38:34,005 <sample.py[InputThread]:DEBUG> Received 115 bytes: %%<message::false:engine.timer::time=1404221914:nodename=localhost:handlers=tone%z90,yrtp%z90,sip%z90,regfile%z100
    2014-07-01 10:38:34,017 <sample.py[MessageReply(4460148880)]:DEBUG> Received command: libyate.cmd.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1404221914'), ('nodename', 'localhost'), ('handlers', 'tone:90,yrtp:90,sip:90,regfile:100'))))
    2014-07-01 10:38:34,017 <sample.py[MessageReply(4460148880)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x109f7af50>>
    2014-07-01 10:38:34,017 <sample.py[MessageReply(4460148880)]:INFO> Some periodic routine
    2014-07-01 10:38:34,017 <sample.py[MessageReply(4460148880)]:DEBUG> Result: None
    2014-07-01 10:38:34,729 <sample.py[StartupThread]:DEBUG> Removing watcher for "engine.timer"
    2014-07-01 10:38:34,758 <sample.py[OutputThread]:DEBUG> Sending 23 bytes: %%>unwatch:engine.timer
    2014-07-01 10:38:34,764 <sample.py[InputThread]:DEBUG> Received 28 bytes: %%<unwatch:engine.timer:true
    2014-07-01 10:38:34,793 <sample.py[UnWatchReply(4460445008)]:DEBUG> Received command: libyate.cmd.UnWatchReply('engine.timer', True)
    2014-07-01 10:38:34,793 <sample.py[UnWatchReply(4460445008)]:INFO> Removed watcher for "engine.timer"
    ^C2014-07-01 10:38:41,852 <sample.py[MainThread]:INFO> Stopping module
    2014-07-01 10:38:41,852 <sample.py[InputThread]:DEBUG> Stopping input
    2014-07-01 10:38:41,852 <sample.py[MainThread]:DEBUG> Waiting for threads
    2014-07-01 10:38:41,853 <sample.py[InputThread]:INFO> Stopping module


Licensing:
----------

Licensed under ISC license:

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
