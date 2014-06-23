# Python library for developing Yate external modules
A more "pythonic" aproach to Yate.

## Sample script application:
    :::python
    #!/usr/bin/env python
    """
    Sample application to test libyate
    """
    
    import libyate.app
    
    
    class MyApp(libyate.app.YateExtScript):
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

Can be tested passing this lines into stdin:

    :::text
    %%<setlocal:engine.version:5.3.0:true
    %%<install:50:call.route:true
    %%<watch:engine.timer:true
    %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    %%<message::false:engine.timer::time=1403408878:nodename=localhost:handlers=tone%z90,yrtp%z90,sip%z90,regfile%z100
    %%>message:1530541021:1403409825:call.route::id=sip/1:module=sip:status=incoming:answered=false:direction=incoming:caller=test:called=99991001:handlers=regexroute%z100,cdrbuild%z50
    %%<unwatch:engine.timer:true

Expected output:

    :::text
    $ python sample_script.py -d < sample_script_reply.txt >/dev/null
    2014-06-23 17:57:03,691 <sample.py[MainThread]:INFO> Starting module
    2014-06-23 17:57:03,692 <sample.py[InputThread]:DEBUG> Started input
    2014-06-23 17:57:03,692 <sample.py[OutputThread]:DEBUG> Started output
    2014-06-23 17:57:03,693 <sample.py[InputThread]:DEBUG> Received 37 bytes: %%<setlocal:engine.version:5.3.0:true
    2014-06-23 17:57:03,693 <sample.py[StartupThread]:DEBUG> Executing user code
    2014-06-23 17:57:03,693 <sample.py[InputThread]:DEBUG> Received 29 bytes: %%<install:50:call.route:true
    2014-06-23 17:57:03,693 <sample.py[StartupThread]:INFO> Querying parameter "engine.version"
    2014-06-23 17:57:03,694 <sample.py[InputThread]:DEBUG> Received 26 bytes: %%<watch:engine.timer:true
    2014-06-23 17:57:03,697 <sample.py[StartupThread]:INFO> Installing handler for "call.route"
    2014-06-23 17:57:03,698 <sample.py[InputThread]:DEBUG> Received 84 bytes: %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-23 17:57:03,698 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: %%>setlocal:engine.version:
    2014-06-23 17:57:03,698 <sample.py[SetLocalReply(4559903376)]:DEBUG> Received command: libyate.cmd.SetLocalReply('engine.version', '5.3.0', True)
    2014-06-23 17:57:03,699 <sample.py[StartupThread]:DEBUG> Installing watcher for "engine.timer"
    2014-06-23 17:57:03,699 <sample.py[InstallReply(4559904400)]:DEBUG> Received command: libyate.cmd.InstallReply(50, 'call.route', True)
    2014-06-23 17:57:03,699 <sample.py[InputThread]:DEBUG> Received 114 bytes: %%<message::false:engine.timer::time=1403408878:nodename=localhost:handlers=tone%z90,yrtp%z90,sip%z90,regfile%z100
    2014-06-23 17:57:03,701 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: %%>install:50:call.route::
    2014-06-23 17:57:03,701 <sample.py[SetLocalReply(4559903376)]:INFO> Parameter "engine.version" set to: 5.3.0
    2014-06-23 17:57:03,701 <sample.py[StartupThread]:DEBUG> Sending message to the engine: libyate.cmd.Message('somerandomid', datetime.datetime(2014, 6, 23, 20, 57, 3, 701375), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2014-06-23 17:57:03,702 <sample.py[WatchReply(4559921552)]:DEBUG> Received command: libyate.cmd.WatchReply('engine.timer', True)
    2014-06-23 17:57:03,702 <sample.py[InstallReply(4559904400)]:INFO> Installed handler for "call.route"
    2014-06-23 17:57:03,702 <sample.py[MessageReply(4559903888)]:DEBUG> Received command: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-06-23 17:57:03,702 <sample.py[InputThread]:DEBUG> Received 180 bytes: %%>message:1530541021:1403409825:call.route::id=sip/1:module=sip:status=incoming:answered=false:direction=incoming:caller=test:called=99991001:handlers=regexroute%z100,cdrbuild%z50
    2014-06-23 17:57:03,702 <sample.py[OutputThread]:DEBUG> Sending 21 bytes: %%>watch:engine.timer
    2014-06-23 17:57:03,704 <sample.py[WatchReply(4559921552)]:INFO> Installed watcher for "engine.timer"
    2014-06-23 17:57:03,704 <sample.py[MessageReply(4559904336)]:DEBUG> Received command: libyate.cmd.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1403408878'), ('nodename', 'localhost'), ('handlers', 'tone:90,yrtp:90,sip:90,regfile:100'))))
    2014-06-23 17:57:03,704 <sample.py[MessageReply(4559903888)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x10fc85550>>
    2014-06-23 17:57:03,704 <sample.py[InputThread]:DEBUG> Received 28 bytes: %%<unwatch:engine.timer:true
    2014-06-23 17:57:03,705 <sample.py[OutputThread]:DEBUG> Sending 89 bytes: %%>message:somerandomid:1403557023:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-23 17:57:03,705 <sample.py[MessageReply(4559904336)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x10fc85550>>
    2014-06-23 17:57:03,705 <sample.py[MessageReply(4559903888)]:INFO> Got reply for "somerandomid"
    2014-06-23 17:57:03,705 <sample.py[InputThread]:DEBUG> Stopping input
    2014-06-23 17:57:03,706 <sample.py[MessageReply(4559904336)]:INFO> Some periodic routine
    2014-06-23 17:57:03,706 <sample.py[MessageReply(4559903888)]:DEBUG> Result: None
    2014-06-23 17:57:03,706 <sample.py[Message(4559904592)]:DEBUG> Received command: libyate.cmd.Message('1530541021', datetime.datetime(2014, 6, 22, 4, 3, 45), 'call.route', None, libyate.type.OrderedDict((('id', 'sip/1'), ('module', 'sip'), ('status', 'incoming'), ('answered', 'false'), ('direction', 'incoming'), ('caller', 'test'), ('called', '99991001'), ('handlers', 'regexroute:100,cdrbuild:50'))))
    2014-06-23 17:57:03,707 <sample.py[InputThread]:INFO> Stopping module
    2014-06-23 17:57:03,707 <sample.py[UnWatchReply(4559904272)]:DEBUG> Received command: libyate.cmd.UnWatchReply('engine.timer', True)
    2014-06-23 17:57:03,707 <sample.py[MessageReply(4559904336)]:DEBUG> Result: None
    2014-06-23 17:57:03,707 <sample.py[Message(4559904592)]:DEBUG> Handler: <bound method MyApp.call_route of <__main__.MyApp object at 0x10fc85550>>
    2014-06-23 17:57:03,708 <sample.py[UnWatchReply(4559904272)]:INFO> Removed watcher for "engine.timer"
    2014-06-23 17:57:03,708 <sample.py[Message(4559904592)]:INFO> Handling "call.route": libyate.cmd.Message('1530541021', datetime.datetime(2014, 6, 22, 4, 3, 45), 'call.route', None, libyate.type.OrderedDict((('id', 'sip/1'), ('module', 'sip'), ('status', 'incoming'), ('answered', 'false'), ('direction', 'incoming'), ('caller', 'test'), ('called', '99991001'), ('handlers', 'regexroute:100,cdrbuild:50'))))
    2014-06-23 17:57:03,708 <sample.py[MainThread]:DEBUG> Waiting for threads
    2014-06-23 17:57:03,709 <sample.py[Message(4559904592)]:DEBUG> Result: %%<message:1530541021:false:::

## Sample socket client application:
    :::python
    #!/usr/bin/env python
    """
    Sample application to test libyate
    """
    
    import libyate.app
    
    
    class MyApp(libyate.app.YateExtClient):
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
    
        parser = OptionParser()
        parser.add_option('-d', '--debug', action='store_true', default=False,
                          help='increase logging verbosity')
        parser.add_option('-q', '--quiet', action='store_true', default=False,
                          help='reduce the logging verbosity')
        parser.add_option('-H', '--host', default=None,
                          help='connect to host address')
        parser.add_option('-p', '--port', default=None,
                          help='port number')
        parser.add_option('-s', '--socket', default=None,
                          help='connect to unix socket')
    
        options, _ = parser.parse_args()
    
        log_format = \
            '%(asctime)s <%(name)s[%(threadName)s]:%(levelname)s> %(message)s'
    
        logging.basicConfig(**{
            'level': (logging.DEBUG if options.debug else
                      logging.WARN if options.quiet else
                      logging.INFO),
            'format': log_format,
        })
    
        MyApp(options.host or options.socket, options.port, 'sample.py').start()

## Licensing:
Licensed under ISC license:

    :::text
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
