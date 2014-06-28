# Python library for developing Yate external modules

A more "pythonic" aproach to Yate.


## Sample script application:


### extmodule.conf

``` cfg
[scripts]
sample.py=-d
```


### sample.py

``` python
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
```


### Output:

    2014-06-28 10:53:21,078 <sample.py[MainThread]:INFO> Starting module
    2014-06-28 10:53:21,079 <sample.py[InputThread]:DEBUG> Started input
    2014-06-28 10:53:21,079 <sample.py[OutputThread]:DEBUG> Started output
    2014-06-28 10:53:21,080 <sample.py[StartupThread]:DEBUG> Executing user code
    2014-06-28 10:53:21,080 <sample.py[StartupThread]:INFO> Querying parameter "engine.version"
    2014-06-28 10:53:21,084 <sample.py[StartupThread]:INFO> Installing handler for "call.route"
    2014-06-28 10:53:21,085 <sample.py[StartupThread]:DEBUG> Installing watcher for "engine.timer"
    2014-06-28 10:53:21,086 <sample.py[StartupThread]:DEBUG> Sending message to the engine: libyate.cmd.Message('somerandomid', datetime.datetime(2014, 6, 28, 13, 53, 21, 85469), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2014-06-28 10:53:21,089 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: %%>setlocal:engine.version:
    2014-06-28 10:53:21,089 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: %%>install:50:call.route::
    2014-06-28 10:53:21,089 <sample.py[OutputThread]:DEBUG> Sending 21 bytes: %%>watch:engine.timer
    2014-06-28 10:53:21,089 <sample.py[OutputThread]:DEBUG> Sending 89 bytes: %%>message:somerandomid:1403963601:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-28 10:53:21,092 <sample.py[InputThread]:DEBUG> Received 37 bytes: %%<setlocal:engine.version:5.3.0:true
    2014-06-28 10:53:21,092 <sample.py[InputThread]:DEBUG> Received 29 bytes: %%<install:50:call.route:true
    2014-06-28 10:53:21,092 <sample.py[InputThread]:DEBUG> Received 26 bytes: %%<watch:engine.timer:true
    2014-06-28 10:53:21,094 <sample.py[SetLocalReply(4316633488)]:DEBUG> Received command: libyate.cmd.SetLocalReply('engine.version', '5.3.0', True)
    2014-06-28 10:53:21,094 <sample.py[SetLocalReply(4316633488)]:INFO> Parameter "engine.version" set to: 5.3.0
    2014-06-28 10:53:21,094 <sample.py[InstallReply(4314765456)]:DEBUG> Received command: libyate.cmd.InstallReply(50, 'call.route', True)
    2014-06-28 10:53:21,095 <sample.py[InstallReply(4314765456)]:INFO> Installed handler for "call.route"
    2014-06-28 10:53:21,096 <sample.py[WatchReply(4316634704)]:DEBUG> Received command: libyate.cmd.WatchReply('engine.timer', True)
    2014-06-28 10:53:21,096 <sample.py[WatchReply(4316634704)]:INFO> Installed watcher for "engine.timer"
    2014-06-28 10:53:21,098 <sample.py[InputThread]:DEBUG> Received 84 bytes: %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-28 10:53:21,101 <sample.py[MessageReply(4315061584)]:DEBUG> Received command: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-06-28 10:53:21,101 <sample.py[MessageReply(4315061584)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x10149f6d0>>
    2014-06-28 10:53:21,101 <sample.py[MessageReply(4315061584)]:INFO> Got reply for "somerandomid"
    2014-06-28 10:53:21,101 <sample.py[MessageReply(4315061584)]:DEBUG> Result: None
    2014-06-28 10:53:22,002 <sample.py[InputThread]:DEBUG> Received 115 bytes: %%<message::false:engine.timer::time=1403963602:nodename=localhost:handlers=tone%z90,sip%z90,yrtp%z90,regfile%z100
    2014-06-28 10:53:22,028 <sample.py[MessageReply(4314765456)]:DEBUG> Received command: libyate.cmd.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1403963602'), ('nodename', 'localhost'), ('handlers', 'tone:90,sip:90,yrtp:90,regfile:100'))))
    2014-06-28 10:53:22,029 <sample.py[MessageReply(4314765456)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x10149f6d0>>
    2014-06-28 10:53:22,029 <sample.py[MessageReply(4314765456)]:INFO> Some periodic routine
    2014-06-28 10:53:22,029 <sample.py[MessageReply(4314765456)]:DEBUG> Result: None
    2014-06-28 10:53:22,087 <sample.py[StartupThread]:DEBUG> Removing watcher for "engine.timer"
    2014-06-28 10:53:22,118 <sample.py[OutputThread]:DEBUG> Sending 23 bytes: %%>unwatch:engine.timer
    2014-06-28 10:53:22,119 <sample.py[InputThread]:DEBUG> Received 28 bytes: %%<unwatch:engine.timer:true
    2014-06-28 10:53:22,146 <sample.py[UnWatchReply(4315061584)]:DEBUG> Received command: libyate.cmd.UnWatchReply('engine.timer', True)
    2014-06-28 10:53:22,146 <sample.py[UnWatchReply(4315061584)]:INFO> Removed watcher for "engine.timer"


## Sample socket client application:


### extmodule.conf

``` cfg
[listener sample]
type=unix
path=/tmp/sample.sock
```


### sample.py

``` python
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
```


### Expected output:
    $ sample.py -d /tmp/sample.sock 
    2014-06-28 11:09:19,606 <sample.py[MainThread]:INFO> Starting module
    2014-06-28 11:09:19,606 <sample.py[InputThread]:DEBUG> Started input
    2014-06-28 11:09:19,607 <sample.py[OutputThread]:DEBUG> Started output
    2014-06-28 11:09:19,607 <sample.py[StartupThread]:DEBUG> Executing user code
    2014-06-28 11:09:19,607 <sample.py[StartupThread]:INFO> Connecting as "global"
    2014-06-28 11:09:19,610 <sample.py[StartupThread]:DEBUG> Sending output: Starting sample.py
    2014-06-28 11:09:19,610 <sample.py[StartupThread]:INFO> Querying parameter "engine.version"
    2014-06-28 11:09:19,610 <sample.py[StartupThread]:INFO> Installing handler for "call.route"
    2014-06-28 11:09:19,611 <sample.py[StartupThread]:DEBUG> Installing watcher for "engine.timer"
    2014-06-28 11:09:19,612 <sample.py[StartupThread]:DEBUG> Sending message to the engine: libyate.cmd.Message('somerandomid', datetime.datetime(2014, 6, 28, 14, 9, 19, 611479), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2014-06-28 11:09:19,613 <sample.py[OutputThread]:DEBUG> Sending 19 bytes: %%>connect:global::
    2014-06-28 11:09:19,613 <sample.py[OutputThread]:DEBUG> Sending 28 bytes: %%>output:Starting sample.py
    2014-06-28 11:09:19,613 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: %%>setlocal:engine.version:
    2014-06-28 11:09:19,613 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: %%>install:50:call.route::
    2014-06-28 11:09:19,613 <sample.py[OutputThread]:DEBUG> Sending 21 bytes: %%>watch:engine.timer
    2014-06-28 11:09:19,613 <sample.py[OutputThread]:DEBUG> Sending 89 bytes: %%>message:somerandomid:1403964559:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-28 11:09:19,613 <sample.py[InputThread]:DEBUG> Received 37 bytes: %%<setlocal:engine.version:5.3.0:true
    2014-06-28 11:09:19,614 <sample.py[InputThread]:DEBUG> Received 29 bytes: %%<install:50:call.route:true
    2014-06-28 11:09:19,614 <sample.py[InputThread]:DEBUG> Received 26 bytes: %%<watch:engine.timer:true
    2014-06-28 11:09:19,617 <sample.py[SetLocalReply(4325046928)]:DEBUG> Received command: libyate.cmd.SetLocalReply('engine.version', '5.3.0', True)
    2014-06-28 11:09:19,617 <sample.py[SetLocalReply(4325046928)]:INFO> Parameter "engine.version" set to: 5.3.0
    2014-06-28 11:09:19,618 <sample.py[InstallReply(4325048144)]:DEBUG> Received command: libyate.cmd.InstallReply(50, 'call.route', True)
    2014-06-28 11:09:19,618 <sample.py[InputThread]:DEBUG> Received 84 bytes: %%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%
    2014-06-28 11:09:19,618 <sample.py[InstallReply(4325048144)]:INFO> Installed handler for "call.route"
    2014-06-28 11:09:19,619 <sample.py[WatchReply(4325046928)]:DEBUG> Received command: libyate.cmd.WatchReply('engine.timer', True)
    2014-06-28 11:09:19,619 <sample.py[WatchReply(4325046928)]:INFO> Installed watcher for "engine.timer"
    2014-06-28 11:09:19,620 <sample.py[MessageReply(4323433808)]:DEBUG> Received command: libyate.cmd.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2014-06-28 11:09:19,621 <sample.py[MessageReply(4323433808)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x101c9b690>>
    2014-06-28 11:09:19,621 <sample.py[MessageReply(4323433808)]:INFO> Got reply for "somerandomid"
    2014-06-28 11:09:19,621 <sample.py[MessageReply(4323433808)]:DEBUG> Result: None
    2014-06-28 11:09:20,002 <sample.py[InputThread]:DEBUG> Received 115 bytes: %%<message::false:engine.timer::time=1403964560:nodename=localhost:handlers=sip%z90,yrtp%z90,tone%z90,regfile%z100
    2014-06-28 11:09:20,045 <sample.py[MessageReply(4323137680)]:DEBUG> Received command: libyate.cmd.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1403964560'), ('nodename', 'localhost'), ('handlers', 'sip:90,yrtp:90,tone:90,regfile:100'))))
    2014-06-28 11:09:20,046 <sample.py[MessageReply(4323137680)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x101c9b690>>
    2014-06-28 11:09:20,046 <sample.py[MessageReply(4323137680)]:INFO> Some periodic routine
    2014-06-28 11:09:20,046 <sample.py[MessageReply(4323137680)]:DEBUG> Result: None
    2014-06-28 11:09:20,613 <sample.py[StartupThread]:DEBUG> Removing watcher for "engine.timer"
    2014-06-28 11:09:20,641 <sample.py[OutputThread]:DEBUG> Sending 23 bytes: %%>unwatch:engine.timer
    2014-06-28 11:09:20,645 <sample.py[InputThread]:DEBUG> Received 28 bytes: %%<unwatch:engine.timer:true
    2014-06-28 11:09:20,672 <sample.py[UnWatchReply(4323433808)]:DEBUG> Received command: libyate.cmd.UnWatchReply('engine.timer', True)
    2014-06-28 11:09:20,672 <sample.py[UnWatchReply(4323433808)]:INFO> Removed watcher for "engine.timer"
    2014-06-28 11:09:29,432 <sample.py[MainThread]:INFO> Stopping module
    2014-06-28 11:09:29,433 <sample.py[MainThread]:DEBUG> Waiting for threads
    2014-06-28 11:09:29,433 <sample.py[InputThread]:DEBUG> Stopping input
    2014-06-28 11:09:29,435 <sample.py[InputThread]:INFO> Stopping module


## Licensing:

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
