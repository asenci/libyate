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

    import logging
    import optparse

    import libyate.extmodule


    class MyApp(libyate.extmodule.Script):
        def start(self):
            # Query engine version
            self.set_local('engine.version')

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
        parser = optparse.OptionParser()
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

        app = MyApp(name='sample.py', trackparam='libyate_sample', restart=False)
        app.install(app.call_route, 'call.route', 50)
        app.watch(app.timer, 'engine.timer')
        app.main()


* Output:

::

    2015-03-03 18:17:32,374 <sample.py[MainThread]:DEBUG> Setting handler tracking parameter
    2015-03-03 18:17:32,374 <sample.py[MainThread]:INFO> Setting parameter "trackparam" to: libyate_sample
    2015-03-03 18:17:32,375 <sample.py[MainThread]:DEBUG> Setting module restart parameter
    2015-03-03 18:17:32,375 <sample.py[MainThread]:INFO> Setting parameter "restart" to: false
    2015-03-03 18:17:32,375 <sample.py[MainThread]:INFO> Installing handler for "call.route"
    2015-03-03 18:17:32,375 <sample.py[MainThread]:DEBUG> Installing watcher for "engine.timer"
    2015-03-03 18:17:32,375 <sample.py[MainThread]:INFO> Starting module threads
    2015-03-03 18:17:32,375 <sample.py[InputThread]:DEBUG> Started input
    2015-03-03 18:17:32,376 <sample.py[OutputThread]:DEBUG> Started output
    2015-03-03 18:17:32,376 <sample.py[MainLoopThread]:DEBUG> Started main loop
    2015-03-03 18:17:32,376 <sample.py[MainThread]:DEBUG> Dumping the startup queue into the output queue
    2015-03-03 18:17:32,376 <sample.py[MainThread]:DEBUG> Executing user startup code
    2015-03-03 18:17:32,376 <sample.py[MainThread]:INFO> Querying parameter "engine.version"
    2015-03-03 18:17:32,377 <sample.py[MainThread]:DEBUG> Sending message to the engine: libyate.engine.Message('somerandomid', datetime.datetime(2015, 3, 3, 21, 17, 32, 376746), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2015-03-03 18:17:32,377 <sample.py[OutputThread]:DEBUG> Sending 38 bytes: '%%>setlocal:trackparam:libyate_sample\n'
    2015-03-03 18:17:32,378 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: '%%>setlocal:restart:false\n'
    2015-03-03 18:17:32,378 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: '%%>install:50:call.route::\n'
    2015-03-03 18:17:32,378 <sample.py[OutputThread]:DEBUG> Sending 22 bytes: '%%>watch:engine.timer\n'
    2015-03-03 18:17:32,378 <sample.py[OutputThread]:DEBUG> Sending 28 bytes: '%%>setlocal:engine.version:\n'
    2015-03-03 18:17:32,378 <sample.py[OutputThread]:DEBUG> Sending 90 bytes: '%%>message:somerandomid:1425417452:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%\n'
    2015-03-03 18:17:32,378 <sample.py[InputThread]:DEBUG> Received 43 bytes: '%%<setlocal:trackparam:libyate_sample:true\n'
    2015-03-03 18:17:32,380 <sample.py[SetLocalReply(4469319824)]:DEBUG> Received command: libyate.engine.SetLocalReply('trackparam', 'libyate_sample', True)
    2015-03-03 18:17:32,380 <sample.py[SetLocalReply(4469319824)]:INFO> Parameter "trackparam" set to: libyate_sample
    2015-03-03 18:17:32,383 <sample.py[InputThread]:DEBUG> Received 31 bytes: '%%<setlocal:restart:false:true\n'
    2015-03-03 18:17:32,383 <sample.py[InputThread]:DEBUG> Received 30 bytes: '%%<install:50:call.route:true\n'
    2015-03-03 18:17:32,383 <sample.py[InputThread]:DEBUG> Received 27 bytes: '%%<watch:engine.timer:true\n'
    2015-03-03 18:17:32,384 <sample.py[InputThread]:DEBUG> Received 38 bytes: '%%<setlocal:engine.version:5.4.0:true\n'
    2015-03-03 18:17:32,388 <sample.py[SetLocalReply(4474977808)]:DEBUG> Received command: libyate.engine.SetLocalReply('restart', 'false', True)
    2015-03-03 18:17:32,388 <sample.py[InputThread]:DEBUG> Received 85 bytes: '%%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%\n'
    2015-03-03 18:17:32,389 <sample.py[SetLocalReply(4474977808)]:INFO> Parameter "restart" set to: false
    2015-03-03 18:17:32,389 <sample.py[InstallReply(4475147792)]:DEBUG> Received command: libyate.engine.InstallReply(50, 'call.route', True)
    2015-03-03 18:17:32,389 <sample.py[WatchReply(4475148432)]:DEBUG> Received command: libyate.engine.WatchReply('engine.timer', True)
    2015-03-03 18:17:32,390 <sample.py[InstallReply(4475147792)]:INFO> Installed handler for "call.route"
    2015-03-03 18:17:32,390 <sample.py[SetLocalReply(4475149136)]:DEBUG> Received command: libyate.engine.SetLocalReply('engine.version', '5.4.0', True)
    2015-03-03 18:17:32,391 <sample.py[WatchReply(4475148432)]:INFO> Installed watcher for "engine.timer"
    2015-03-03 18:17:32,391 <sample.py[SetLocalReply(4475149136)]:INFO> Parameter "engine.version" set to: 5.4.0
    2015-03-03 18:17:32,391 <sample.py[MessageReply(4475149648)]:DEBUG> Received command: libyate.engine.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2015-03-03 18:17:32,392 <sample.py[MessageReply(4475149648)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x10ababa50>>
    2015-03-03 18:17:32,392 <sample.py[MessageReply(4475149648)]:INFO> Got reply for "somerandomid"
    2015-03-03 18:17:32,392 <sample.py[MessageReply(4475149648)]:DEBUG> Result: None
    2015-03-03 18:17:33,018 <sample.py[InputThread]:DEBUG> Received 589 bytes: '%%<message::false:engine.timer::time=1425417453:nodename=hades:handlers=subscription%z90,zlibcompress%z90,socks%z90,openssl%z90,mux%z90,javascript%z90,callfork%z90,conf%z90,dumb%z90,enumroute%z90,gvoice%z90,pbx%z90,iax%z90,jingle%z90,mgcpgw%z90,mrcp%z90,monitoring%z90,park%z90,queues%z90,sipfeatures%z90,users%z90,snmpagent%z90,fileinfo%z90,filetransfer%z90,stun%z90,analog%z90,sig%z90,jbfeatures%z90,jabber%z90,sigtransport%z90,mgcpca%z90,ciscosm%z90,analogdetect%z90,tonedetect%z90,tone%z90,yrtp%z90,analyzer%z90,wave%z90,sip%z90,presence%z90,queuesnotify%z90,register%z90,regfile%z100\n'
    2015-03-03 18:17:33,053 <sample.py[MessageReply(4469319824)]:DEBUG> Received command: libyate.engine.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1425417453'), ('nodename', 'hades'), ('handlers', 'subscription:90,zlibcompress:90,socks:90,openssl:90,mux:90,javascript:90,callfork:90,conf:90,dumb:90,enumroute:90,gvoice:90,pbx:90,iax:90,jingle:90,mgcpgw:90,mrcp:90,monitoring:90,park:90,queues:90,sipfeatures:90,users:90,snmpagent:90,fileinfo:90,filetransfer:90,stun:90,analog:90,sig:90,jbfeatures:90,jabber:90,sigtransport:90,mgcpca:90,ciscosm:90,analogdetect:90,tonedetect:90,tone:90,yrtp:90,analyzer:90,wave:90,sip:90,presence:90,queuesnotify:90,register:90,regfile:100'))))
    2015-03-03 18:17:33,053 <sample.py[MessageReply(4469319824)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x10ababa50>>
    2015-03-03 18:17:33,053 <sample.py[MessageReply(4469319824)]:INFO> Some periodic routine
    2015-03-03 18:17:33,053 <sample.py[MessageReply(4469319824)]:DEBUG> Result: None
    2015-03-03 18:17:33,382 <sample.py[MainThread]:DEBUG> Removing watcher for "engine.timer"
    2015-03-03 18:17:33,383 <sample.py[MainThread]:DEBUG> Entering main loop
    2015-03-03 18:17:33,417 <sample.py[OutputThread]:DEBUG> Sending 24 bytes: '%%>unwatch:engine.timer\n'
    2015-03-03 18:17:33,422 <sample.py[InputThread]:DEBUG> Received 29 bytes: '%%<unwatch:engine.timer:true\n'
    2015-03-03 18:17:33,451 <sample.py[UnWatchReply(4469419408)]:DEBUG> Received command: libyate.engine.UnWatchReply('engine.timer', True)
    2015-03-03 18:17:33,452 <sample.py[UnWatchReply(4469419408)]:INFO> Removed watcher for "engine.timer"
    2015-03-03 18:17:49,969 <sample.py[InputThread]:DEBUG> Stopping input
    2015-03-03 18:17:49,969 <sample.py[InputThread]:INFO> Stopping module
    2015-03-03 18:17:49,970 <sample.py[MainThread]:INFO> Stopping module
    2015-03-03 18:17:50,012 <sample.py[OutputThread]:INFO> Stopping module
    2015-03-03 18:17:50,024 <sample.py[MainThread]:DEBUG> Waiting for threads


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

    import logging
    import optparse

    import libyate.extmodule


    class MyApp(libyate.extmodule.SocketClient):
        def start(self):
            # Send message to the engine
            self.output('Starting sample.py')

            # Query engine version
            self.set_local('engine.version')

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
        parser = optparse.OptionParser(
            'usage: %prog [options] <host or path> [port]')
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

        app = MyApp('global', *args, name='sample.py', trackparam='libyate_sample',
                    restart=False)
        app.install(app.call_route, 'call.route', 50)
        app.watch(app.timer, 'engine.timer')
        app.main()


* Expected output:

::

    $ python sample_client.py -d 127.0.0.1 5555
    2015-03-03 18:30:35,476 <sample.py[MainThread]:DEBUG> Setting handler tracking parameter
    2015-03-03 18:30:35,476 <sample.py[MainThread]:INFO> Setting parameter "trackparam" to: libyate_sample
    2015-03-03 18:30:35,477 <sample.py[MainThread]:DEBUG> Setting module restart parameter
    2015-03-03 18:30:35,477 <sample.py[MainThread]:INFO> Setting parameter "restart" to: false
    2015-03-03 18:30:35,477 <sample.py[MainThread]:INFO> Connecting as "global"
    2015-03-03 18:30:35,478 <sample.py[MainThread]:INFO> Installing handler for "call.route"
    2015-03-03 18:30:35,478 <sample.py[MainThread]:DEBUG> Installing watcher for "engine.timer"
    2015-03-03 18:30:35,478 <sample.py[MainThread]:INFO> Starting module threads
    2015-03-03 18:30:35,479 <sample.py[InputThread]:DEBUG> Started input
    2015-03-03 18:30:35,479 <sample.py[OutputThread]:DEBUG> Started output
    2015-03-03 18:30:35,479 <sample.py[OutputThread]:DEBUG> Sending 20 bytes: '%%>connect:global::\n'
    2015-03-03 18:30:35,479 <sample.py[MainLoopThread]:DEBUG> Started main loop
    2015-03-03 18:30:35,479 <sample.py[MainThread]:DEBUG> Dumping the startup queue into the output queue
    2015-03-03 18:30:35,480 <sample.py[MainThread]:DEBUG> Executing user startup code
    2015-03-03 18:30:35,480 <sample.py[MainThread]:DEBUG> Sending output: Starting sample.py
    2015-03-03 18:30:35,480 <sample.py[MainThread]:INFO> Querying parameter "engine.version"
    2015-03-03 18:30:35,481 <sample.py[MainThread]:DEBUG> Sending message to the engine: libyate.engine.Message('somerandomid', datetime.datetime(2015, 3, 3, 21, 30, 35, 480296), 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', True), ('done', '75%'))))
    2015-03-03 18:30:35,481 <sample.py[OutputThread]:DEBUG> Sending 38 bytes: '%%>setlocal:trackparam:libyate_sample\n'
    2015-03-03 18:30:35,481 <sample.py[OutputThread]:DEBUG> Sending 26 bytes: '%%>setlocal:restart:false\n'
    2015-03-03 18:30:35,481 <sample.py[OutputThread]:DEBUG> Sending 27 bytes: '%%>install:50:call.route::\n'
    2015-03-03 18:30:35,482 <sample.py[OutputThread]:DEBUG> Sending 22 bytes: '%%>watch:engine.timer\n'
    2015-03-03 18:30:35,482 <sample.py[OutputThread]:DEBUG> Sending 29 bytes: '%%>output:Starting sample.py\n'
    2015-03-03 18:30:35,482 <sample.py[OutputThread]:DEBUG> Sending 28 bytes: '%%>setlocal:engine.version:\n'
    2015-03-03 18:30:35,482 <sample.py[OutputThread]:DEBUG> Sending 90 bytes: '%%>message:somerandomid:1425418235:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%\n'
    2015-03-03 18:30:35,484 <sample.py[InputThread]:DEBUG> Received 42 bytes: '%%<setlocal:trackparam:libyate_sample:true'
    2015-03-03 18:30:35,484 <sample.py[InputThread]:DEBUG> Received 127 bytes: '\n%%<setlocal:restart:false:true\n%%<install:50:call.route:true\n%%<watch:engine.timer:true\n%%<setlocal:engine.version:5.4.0:true\n'
    2015-03-03 18:30:35,489 <sample.py[SetLocalReply(4313939920)]:DEBUG> Received command: libyate.engine.SetLocalReply('trackparam', 'libyate_sample', True)
    2015-03-03 18:30:35,489 <sample.py[SetLocalReply(4313939920)]:INFO> Parameter "trackparam" set to: libyate_sample
    2015-03-03 18:30:35,490 <sample.py[InputThread]:DEBUG> Received 84 bytes: '%%<message:somerandomid:false:myapp.test::path=/bin%z/usr/bin:testing=true:done=75%%'
    2015-03-03 18:30:35,490 <sample.py[SetLocalReply(4313939856)]:DEBUG> Received command: libyate.engine.SetLocalReply('restart', 'false', True)
    2015-03-03 18:30:35,490 <sample.py[InputThread]:DEBUG> Received 1 bytes: '\n'
    2015-03-03 18:30:35,490 <sample.py[SetLocalReply(4313939856)]:INFO> Parameter "restart" set to: false
    2015-03-03 18:30:35,491 <sample.py[InstallReply(4313939792)]:DEBUG> Received command: libyate.engine.InstallReply(50, 'call.route', True)
    2015-03-03 18:30:35,491 <sample.py[InstallReply(4313939792)]:INFO> Installed handler for "call.route"
    2015-03-03 18:30:35,492 <sample.py[WatchReply(4313939920)]:DEBUG> Received command: libyate.engine.WatchReply('engine.timer', True)
    2015-03-03 18:30:35,492 <sample.py[WatchReply(4313939920)]:INFO> Installed watcher for "engine.timer"
    2015-03-03 18:30:35,492 <sample.py[SetLocalReply(4313939856)]:DEBUG> Received command: libyate.engine.SetLocalReply('engine.version', '5.4.0', True)
    2015-03-03 18:30:35,492 <sample.py[SetLocalReply(4313939856)]:INFO> Parameter "engine.version" set to: 5.4.0
    2015-03-03 18:30:35,493 <sample.py[MessageReply(4309208784)]:DEBUG> Received command: libyate.engine.MessageReply('somerandomid', False, 'myapp.test', None, libyate.type.OrderedDict((('path', '/bin:/usr/bin'), ('testing', 'true'), ('done', '75%'))))
    2015-03-03 18:30:35,493 <sample.py[MessageReply(4309208784)]:DEBUG> Handler: <bound method MyApp.reply of <__main__.MyApp object at 0x101217bd0>>
    2015-03-03 18:30:35,493 <sample.py[MessageReply(4309208784)]:INFO> Got reply for "somerandomid"
    2015-03-03 18:30:35,493 <sample.py[MessageReply(4309208784)]:DEBUG> Result: None
    2015-03-03 18:30:36,001 <sample.py[InputThread]:DEBUG> Received 589 bytes: '%%<message::false:engine.timer::time=1425418236:nodename=hades:handlers=subscription%z90,zlibcompress%z90,socks%z90,openssl%z90,mux%z90,javascript%z90,callfork%z90,conf%z90,dumb%z90,enumroute%z90,gvoice%z90,pbx%z90,iax%z90,jingle%z90,mgcpgw%z90,mrcp%z90,monitoring%z90,park%z90,queues%z90,sipfeatures%z90,users%z90,snmpagent%z90,fileinfo%z90,filetransfer%z90,stun%z90,analog%z90,sig%z90,jbfeatures%z90,jabber%z90,sigtransport%z90,mgcpca%z90,ciscosm%z90,analogdetect%z90,tonedetect%z90,tone%z90,yrtp%z90,analyzer%z90,wave%z90,sip%z90,presence%z90,queuesnotify%z90,register%z90,regfile%z100\n'
    2015-03-03 18:30:36,048 <sample.py[MessageReply(4313939792)]:DEBUG> Received command: libyate.engine.MessageReply(None, False, 'engine.timer', None, libyate.type.OrderedDict((('time', '1425418236'), ('nodename', 'hades'), ('handlers', 'subscription:90,zlibcompress:90,socks:90,openssl:90,mux:90,javascript:90,callfork:90,conf:90,dumb:90,enumroute:90,gvoice:90,pbx:90,iax:90,jingle:90,mgcpgw:90,mrcp:90,monitoring:90,park:90,queues:90,sipfeatures:90,users:90,snmpagent:90,fileinfo:90,filetransfer:90,stun:90,analog:90,sig:90,jbfeatures:90,jabber:90,sigtransport:90,mgcpca:90,ciscosm:90,analogdetect:90,tonedetect:90,tone:90,yrtp:90,analyzer:90,wave:90,sip:90,presence:90,queuesnotify:90,register:90,regfile:100'))))
    2015-03-03 18:30:36,048 <sample.py[MessageReply(4313939792)]:DEBUG> Handler: <bound method MyApp.timer of <__main__.MyApp object at 0x101217bd0>>
    2015-03-03 18:30:36,048 <sample.py[MessageReply(4313939792)]:INFO> Some periodic routine
    2015-03-03 18:30:36,049 <sample.py[MessageReply(4313939792)]:DEBUG> Result: None
    2015-03-03 18:30:36,484 <sample.py[MainThread]:DEBUG> Removing watcher for "engine.timer"
    2015-03-03 18:30:36,484 <sample.py[MainThread]:DEBUG> Entering main loop
    2015-03-03 18:30:36,520 <sample.py[OutputThread]:DEBUG> Sending 24 bytes: '%%>unwatch:engine.timer\n'
    2015-03-03 18:30:36,525 <sample.py[InputThread]:DEBUG> Received 29 bytes: '%%<unwatch:engine.timer:true\n'
    2015-03-03 18:30:36,551 <sample.py[UnWatchReply(4309208784)]:DEBUG> Received command: libyate.engine.UnWatchReply('engine.timer', True)
    2015-03-03 18:30:36,551 <sample.py[UnWatchReply(4309208784)]:INFO> Removed watcher for "engine.timer"
    ^C2015-03-03 18:30:41,455 <sample.py[MainThread]:INFO> Stopping module
    2015-03-03 18:30:41,455 <sample.py[InputThread]:DEBUG> Stopping input
    2015-03-03 18:30:41,455 <sample.py[InputThread]:INFO> Stopping module
    2015-03-03 18:30:41,467 <sample.py[OutputThread]:INFO> Stopping module
    2015-03-03 18:30:41,510 <sample.py[MainThread]:DEBUG> Waiting for threads


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
