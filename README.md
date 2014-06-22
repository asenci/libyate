# Python library for developing Yate external modules
A more "pythonic" aproach to Yate.

## Sample application:

    :::python
    #!/usr/bin/env python
    import libyate.app

    class MyApp(libyate.app.YateExtScript):
        def run(self):
            from time import sleep
    
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
    
            sleep(1)
            self.unwatch('engine.timer')
    
        def call_route(self, msg):
            self.logger.info('Handling "call.route": {0!r}'.format(msg))
    
            # Just reply with processed = False
            return msg.reply()
    
        def reply(self, msg):
            self.logger.info('Got result: {0!r}'.format(msg))
    
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
    
        MyApp('sample.MyApp').start()

Can be tested passing this lines into stdin:

    :::text
    %%<setlocal:engine.version:5.3.0:true
    %%<install:50:call.route:true
    %%<watch:engine.timer:true
    %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    %%<message::false:engine.timer::time=1403408878:nodename=hades.home:handlers=tone%z90,yrtp%z90,sip%z90,regfile%z100
    %%>message:1530541021:1403409825:call.route::id=sip/1:module=sip:status=incoming:answered=false:direction=incoming:caller=test:called=99991001:handlers=regexroute%z100,cdrbuild%z50
    %%<unwatch:engine.timer:true

Expected output:

    :::text
    $ python sample.py -d < sample_reply.txt >/dev/null
    2014-06-22 01:06:57,117 <sample.py[MainThread]:INFO> Starting module
    2014-06-22 01:06:57,117 <sample.py[StartupThread]:DEBUG> Starting output handler thread
    2014-06-22 01:06:57,117 <sample.py[MainThread]:DEBUG> Started input
    2014-06-22 01:06:57,118 <sample.py[OutputThread]:DEBUG> Started output
    2014-06-22 01:06:57,118 <sample.py[StartupThread]:DEBUG> Executing user code
    2014-06-22 01:06:57,118 <sample.py[MainThread]:DEBUG> Received: %%<setlocal:engine.version:5.3.0:true
    2014-06-22 01:06:57,118 <sample.py[StartupThread]:INFO> Querying parameter "engine.version"
    2014-06-22 01:06:57,121 <sample.py[SetLocalReply(4556365712)]:DEBUG> Received command: libyate.cmd.SetLocalReply('engine.version', '5.3.0', True)
    2014-06-22 01:06:57,121 <sample.py[StartupThread]:INFO> Installing handler for "call.route"
    2014-06-22 01:06:57,121 <sample.py[SetLocalReply(4556365712)]:INFO> Parameter "engine.version" set to: 5.3.0
    2014-06-22 01:06:57,121 <sample.py[OutputThread]:DEBUG> Sending: %%>setlocal:engine.version:
    2014-06-22 01:06:57,121 <sample.py[MainThread]:DEBUG> Received: %%<install:50:call.route:true
    2014-06-22 01:06:57,121 <sample.py[StartupThread]:DEBUG> Installing watcher for "engine.timer"
    2014-06-22 01:06:57,122 <sample.py[OutputThread]:DEBUG> Sending: %%>install:50:call.route::
    2014-06-22 01:06:57,123 <sample.py[InstallReply(4556365328)]:DEBUG> Received command: libyate.cmd.InstallReply(50, 'call.route', True)
    2014-06-22 01:06:57,123 <sample.py[MainThread]:DEBUG> Received: %%<watch:engine.timer:true
    2014-06-22 01:06:57,123 <sample.py[StartupThread]:DEBUG> Sending message to the engine: libyate.cmd.Message('somerandomid', datetime.datetime(2014, 6, 22, 4, 6, 57, 123351), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2014-06-22 01:06:57,124 <sample.py[OutputThread]:DEBUG> Sending: %%>watch:engine.timer
    2014-06-22 01:06:57,124 <sample.py[InstallReply(4556365328)]:INFO> Installed handler for "call.route"
    2014-06-22 01:06:57,125 <sample.py[WatchReply(4564915536)]:DEBUG> Received command: libyate.cmd.WatchReply('engine.timer', True)
    2014-06-22 01:06:57,125 <sample.py[MainThread]:DEBUG> Received: %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-22 01:06:57,125 <sample.py[WatchReply(4564915536)]:INFO> Installed watcher for "engine.timer"
    2014-06-22 01:06:57,126 <sample.py[OutputThread]:DEBUG> Sending: %%>message:somerandomid:1403410017:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-22 01:06:57,127 <sample.py[MessageReply(4554668176)]:DEBUG> Received command: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-06-22 01:06:57,127 <sample.py[MainThread]:DEBUG> Received: %%<message::false:engine.timer::time=1403408878:nodename=hades.home:handlers=tone%z90,yrtp%z90,sip%z90,regfile%z100
    2014-06-22 01:06:57,128 <sample.py[MessageReply(4554668176)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x10f949110>>
    2014-06-22 01:06:57,128 <sample.py[MessageReply(4556365776)]:DEBUG> Received command: libyate.cmd.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1403408878'), ('nodename', 'hades.home'), ('handlers', 'tone:90,yrtp:90,sip:90,regfile:100'))))
    2014-06-22 01:06:57,128 <sample.py[MainThread]:DEBUG> Received: %%>message:1530541021:1403409825:call.route::id=sip/1:module=sip:status=incoming:answered=false:direction=incoming:caller=test:called=99991001:handlers=regexroute%z100,cdrbuild%z50
    2014-06-22 01:06:57,128 <sample.py[MessageReply(4554668176)]:INFO> Got result: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-06-22 01:06:57,129 <sample.py[MessageReply(4556365776)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x10f949110>>
    2014-06-22 01:06:57,129 <sample.py[MessageReply(4554668176)]:DEBUG> Result: None
    2014-06-22 01:06:57,129 <sample.py[Message(4564916048)]:DEBUG> Received command: libyate.cmd.Message('1530541021', datetime.datetime(2014, 6, 22, 4, 3, 45), 'call.route', None, libyate.type.OrderedDict((('id', 'sip/1'), ('module', 'sip'), ('status', 'incoming'), ('answered', 'false'), ('direction', 'incoming'), ('caller', 'test'), ('called', '99991001'), ('handlers', 'regexroute:100,cdrbuild:50'))))
    2014-06-22 01:06:57,130 <sample.py[MainThread]:DEBUG> Received: %%<unwatch:engine.timer:true
    2014-06-22 01:06:57,130 <sample.py[MessageReply(4556365776)]:INFO> Some periodic routine
    2014-06-22 01:06:57,130 <sample.py[Message(4564916048)]:DEBUG> Handler: <bound method MyApp.call_route of <__main__.MyApp object at 0x10f949110>>
    2014-06-22 01:06:57,130 <sample.py[MessageReply(4556365776)]:DEBUG> Result: None
    2014-06-22 01:06:57,131 <sample.py[UnWatchReply(4556365712)]:DEBUG> Received command: libyate.cmd.UnWatchReply('engine.timer', True)
    2014-06-22 01:06:57,131 <sample.py[Message(4564916048)]:INFO> Handling "call.route": libyate.cmd.Message('1530541021', datetime.datetime(2014, 6, 22, 4, 3, 45), 'call.route', None, libyate.type.OrderedDict((('id', 'sip/1'), ('module', 'sip'), ('status', 'incoming'), ('answered', 'false'), ('direction', 'incoming'), ('caller', 'test'), ('called', '99991001'), ('handlers', 'regexroute:100,cdrbuild:50'))))
    2014-06-22 01:06:57,131 <sample.py[MainThread]:INFO> Stopped input
    2014-06-22 01:06:57,131 <sample.py[UnWatchReply(4556365712)]:INFO> Removed watcher for "engine.timer"
    2014-06-22 01:06:57,132 <sample.py[Message(4564916048)]:DEBUG> Result: %%<message:1530541021:false:::
    2014-06-22 01:06:57,132 <sample.py[MainThread]:DEBUG> Waiting for threads
    2014-06-22 01:06:57,132 <sample.py[OutputThread]:DEBUG> Sending: %%<message:1530541021:false:::
    2014-06-22 01:06:58,126 <sample.py[StartupThread]:DEBUG> Removing watcher for "engine.timer"
    2014-06-22 01:06:58,126 <sample.py[OutputThread]:DEBUG> Sending: %%>unwatch:engine.timer



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
