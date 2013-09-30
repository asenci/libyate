# Python library for developing Yate external modules
A more "pythonic" aproach to Yate.

## Sample application:

    :::python
    #!/usr/bin/env python
    import libyate
    from optparse import OptionParser

    class my_app(libyate.YateExtModule):
        def handle_start(self):
            self.set_local('testing', 'true')
            self.install('test', priority=50)
            self.install('engine.timer')
            self.watch('call.route')
            self.message(
                name='app.job',
                id='myapp55251',
                kvp={
                    'job': 'cleanup', 'done': '75%', 'path': '/bin:/usr/bin'
                })
            self.uninstall('test')
            self.uninstall('engine.timer')
            self.unwatch('call.route')

    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true',
                      help='increase logging verbosity')
    parser.add_option('-q', '--quiet', action='store_true',
                      help='reduce the logging verbosity')
    parser.add_option('-n', '--name', default=__file__,
                      help='name used for logging')

    my_app(**vars(parser.parse_args()[0])).run()

Can be tested passing this lines into stdin:

    :::text
    %%<setlocal:testing:true:true
    %%<install:50:test:true
    %%<install:100:engine.timer:true
    %%<message:myapp55251:true:app.job:Restart required:path=/bin%z/usr/bin%z/usr/local/bin
    %%>message:234479208:1095112795:engine.timer::time=1095112795
    %%>message:234479288:1095112796:engine.timer::time=1095112796
    %%>message:234479244:1095112797:engine.timer::time=1095112797
    %%<uninstall:50:test:false
    %%<uninstall:100:engine.timer:true
    %%<uninstall:100:engine.timer:true
    %%>message:234479244:1095112797:engine.test:false:testing=true
    %%<unwatch:call.route:true
    Error in:%%>watch:call.route
    %%>teste:234479244:1095112797:engine.test:false

Expected output:

    :::text
    $ python sample.py -d < sample_reply.txt >/dev/null
    2013-09-30 15:20:16,408 <sample.py[MainThread]:INFO> Loading module
    2013-09-30 15:20:16,408 <sample.py[MainThread]:DEBUG> Starting output queue handler
    2013-09-30 15:20:16,408 <sample.py[OutputHandler]:INFO> Starting
    2013-09-30 15:20:16,409 <sample.py[MainThread]:DEBUG> Starting input queue handler
    2013-09-30 15:20:16,409 <sample.py[InputHandler]:INFO> Starting
    2013-09-30 15:20:16,409 <sample.py[MainThread]:DEBUG> Running startup handler
    2013-09-30 15:20:16,409 <sample.py[MainThread]:DEBUG> Setting parameter "testing": "true"
    2013-09-30 15:20:16,411 <sample.py[MainThread]:DEBUG> Installing handler for "test"
    2013-09-30 15:20:16,411 <sample.py[MainThread]:DEBUG> Installing handler for "engine.timer"
    2013-09-30 15:20:16,411 <sample.py[OutputHandler]:DEBUG> Received command: %%>setlocal:testing:true
    2013-09-30 15:20:16,412 <sample.py[MainThread]:DEBUG> Installing watcher for "call.route"
    2013-09-30 15:20:16,412 <sample.py[OutputHandler]:DEBUG> Sending: %%>setlocal:testing:true
    2013-09-30 15:20:16,412 <sample.py[MainThread]:DEBUG> Sending message: "app.job"
    2013-09-30 15:20:16,412 <sample.py[OutputHandler]:DEBUG> Received command: %%>install:50:test
    2013-09-30 15:20:16,413 <sample.py[MainThread]:DEBUG> Uninstalling handler for "test"
    2013-09-30 15:20:16,413 <sample.py[OutputHandler]:DEBUG> Sending: %%>install:50:test
    2013-09-30 15:20:16,413 <sample.py[MainThread]:DEBUG> Uninstalling handler for "engine.timer"
    2013-09-30 15:20:16,413 <sample.py[OutputHandler]:DEBUG> Received command: %%>install::engine.timer
    2013-09-30 15:20:16,413 <sample.py[MainThread]:DEBUG> Uninstalling watcher for "call.route"
    2013-09-30 15:20:16,413 <sample.py[OutputHandler]:DEBUG> Sending: %%>install::engine.timer
    2013-09-30 15:20:16,414 <sample.py[MainThread]:DEBUG> Entering main loop
    2013-09-30 15:20:16,414 <sample.py[OutputHandler]:DEBUG> Received command: %%>watch:call.route
    2013-09-30 15:20:16,414 <sample.py[MainThread]:DEBUG> Received: %%<setlocal:testing:true:true
    2013-09-30 15:20:16,414 <sample.py[OutputHandler]:DEBUG> Sending: %%>watch:call.route
    2013-09-30 15:20:16,414 <sample.py[MainThread]:DEBUG> Received: %%<install:50:test:true
    2013-09-30 15:20:16,415 <sample.py[InputHandler]:DEBUG> Received command: %%<setlocal:testing:true:true
    2013-09-30 15:20:16,415 <sample.py[OutputHandler]:DEBUG> Received command: %%>message:myapp55251:1380565216:app.job::path=/bin%z/usr/bin:job=cleanup:done=75%%
    2013-09-30 15:20:16,415 <sample.py[MainThread]:DEBUG> Received: %%<install:100:engine.timer:true
    2013-09-30 15:20:16,415 <sample.py[InputHandler]:DEBUG> Starting handler: setlocal/testing
    2013-09-30 15:20:16,416 <sample.py[OutputHandler]:DEBUG> Sending: %%>message:myapp55251:1380565216:app.job::path=/bin%z/usr/bin:job=cleanup:done=75%%
    2013-09-30 15:20:16,416 <sample.py[MainThread]:DEBUG> Received: %%<message:myapp55251:true:app.job:Restart required:path=/bin%z/usr/bin%z/usr/local/bin
    2013-09-30 15:20:16,416 <sample.py[setlocal/testing]:DEBUG> Processing command: %%<setlocal:testing:true:true
    2013-09-30 15:20:16,417 <sample.py[OutputHandler]:DEBUG> Received command: %%>uninstall:test
    2013-09-30 15:20:16,417 <sample.py[InputHandler]:DEBUG> Received command: %%<install:50:test:true
    2013-09-30 15:20:16,417 <sample.py[MainThread]:DEBUG> Received: %%>message:234479208:1095112795:engine.timer::time=1095112795
    2013-09-30 15:20:16,417 <sample.py[setlocal/testing]:DEBUG> Command executed successfully: %%>setlocal:testing:true
    2013-09-30 15:20:16,417 <sample.py[OutputHandler]:DEBUG> Sending: %%>uninstall:test
    2013-09-30 15:20:16,417 <sample.py[InputHandler]:DEBUG> Starting handler: install/test
    2013-09-30 15:20:16,418 <sample.py[MainThread]:DEBUG> Received: %%>message:234479288:1095112796:engine.timer::time=1095112796
    2013-09-30 15:20:16,418 <sample.py[OutputHandler]:DEBUG> Received command: %%>uninstall:engine.timer
    2013-09-30 15:20:16,418 <sample.py[install/test]:DEBUG> Processing command: %%<install:50:test:true
    2013-09-30 15:20:16,418 <sample.py[InputHandler]:DEBUG> Received command: %%<install:100:engine.timer:true
    2013-09-30 15:20:16,419 <sample.py[MainThread]:DEBUG> Received: %%>message:234479244:1095112797:engine.timer::time=1095112797
    2013-09-30 15:20:16,419 <sample.py[OutputHandler]:DEBUG> Sending: %%>uninstall:engine.timer
    2013-09-30 15:20:16,419 <sample.py[install/test]:DEBUG> Command executed successfully: %%>install:50:test
    2013-09-30 15:20:16,419 <sample.py[InputHandler]:DEBUG> Removed finished thread: setlocal/testing
    2013-09-30 15:20:16,419 <sample.py[MainThread]:DEBUG> Received: %%<uninstall:50:test:false
    2013-09-30 15:20:16,420 <sample.py[InputHandler]:DEBUG> Starting handler: install/engine.timer
    2013-09-30 15:20:16,420 <sample.py[OutputHandler]:DEBUG> Received command: %%>unwatch:call.route
    2013-09-30 15:20:16,420 <sample.py[MainThread]:DEBUG> Received: %%<uninstall:100:engine.timer:true
    2013-09-30 15:20:16,420 <sample.py[install/engine.timer]:DEBUG> Processing command: %%<install:100:engine.timer:true
    2013-09-30 15:20:16,421 <sample.py[InputHandler]:DEBUG> Received command: %%<message:myapp55251:true:app.job:Restart required:path=/bin%z/usr/bin%z/usr/local/bin
    2013-09-30 15:20:16,421 <sample.py[OutputHandler]:DEBUG> Sending: %%>unwatch:call.route
    2013-09-30 15:20:16,421 <sample.py[MainThread]:DEBUG> Received: %%<uninstall:100:engine.timer:true
    2013-09-30 15:20:16,421 <sample.py[install/engine.timer]:DEBUG> Command executed successfully: %%>install::engine.timer
    2013-09-30 15:20:16,421 <sample.py[InputHandler]:DEBUG> Removed finished thread: install/test
    2013-09-30 15:20:16,422 <sample.py[MainThread]:DEBUG> Received: %%>message:234479244:1095112797:engine.test:false:testing=true
    2013-09-30 15:20:16,422 <sample.py[InputHandler]:DEBUG> Starting handler: message/myapp55251
    2013-09-30 15:20:16,422 <sample.py[MainThread]:DEBUG> Received: %%<unwatch:call.route:true
    2013-09-30 15:20:16,423 <sample.py[MainThread]:DEBUG> Received: Error in:%%>watch:call.route
    2013-09-30 15:20:16,423 <sample.py[message/myapp55251]:DEBUG> Processing command: %%<message:myapp55251:true:app.job:Restart required:path=/bin%z/usr/bin%z/usr/local/bin
    2013-09-30 15:20:16,423 <sample.py[MainThread]:DEBUG> Received: %%>teste:234479244:1095112797:engine.test:false
    2013-09-30 15:20:16,423 <sample.py[InputHandler]:DEBUG> Received command: %%>message:234479208:1095112795:engine.timer::time=1095112795
    2013-09-30 15:20:16,424 <sample.py[message/myapp55251]:DEBUG> Command executed successfully: %%>message:myapp55251:1380565216:app.job::path=/bin%z/usr/bin:job=cleanup:done=75%%
    2013-09-30 15:20:16,424 <sample.py[MainThread]:ERROR> Command method "%%>teste" not implemented
    2013-09-30 15:20:16,424 <sample.py[InputHandler]:DEBUG> Removed finished thread: install/engine.timer
    2013-09-30 15:20:16,424 <sample.py[MainThread]:INFO> Running shutdown handler
    2013-09-30 15:20:16,424 <sample.py[InputHandler]:DEBUG> Starting handler: message/234479208
    2013-09-30 15:20:16,425 <sample.py[MainThread]:DEBUG> Module shutdown
    2013-09-30 15:20:16,425 <sample.py[MainThread]:DEBUG> Shutting down input queue
    2013-09-30 15:20:16,425 <sample.py[message/234479208]:DEBUG> Processing command: %%>message:234479208:1095112795:engine.timer::time=1095112795
    2013-09-30 15:20:16,425 <sample.py[MainThread]:DEBUG> Waiting for input queue handler
    2013-09-30 15:20:16,425 <sample.py[InputHandler]:DEBUG> Received command: %%>message:234479288:1095112796:engine.timer::time=1095112796
    2013-09-30 15:20:16,425 <sample.py[message/234479208]:DEBUG> No action defined, replying without processing
    2013-09-30 15:20:16,426 <sample.py[InputHandler]:DEBUG> Removed finished thread: message/myapp55251
    2013-09-30 15:20:16,426 <sample.py[OutputHandler]:DEBUG> Received command: %%<message:234479208:false:engine.timer::time=1095112795
    2013-09-30 15:20:16,426 <sample.py[InputHandler]:DEBUG> Starting handler: message/234479288
    2013-09-30 15:20:16,426 <sample.py[OutputHandler]:DEBUG> Sending: %%<message:234479208:false:engine.timer::time=1095112795
    2013-09-30 15:20:16,427 <sample.py[message/234479288]:DEBUG> Processing command: %%>message:234479288:1095112796:engine.timer::time=1095112796
    2013-09-30 15:20:16,427 <sample.py[InputHandler]:DEBUG> Received command: %%>message:234479244:1095112797:engine.timer::time=1095112797
    2013-09-30 15:20:16,427 <sample.py[message/234479288]:DEBUG> No action defined, replying without processing
    2013-09-30 15:20:16,427 <sample.py[InputHandler]:DEBUG> Removed finished thread: message/234479208
    2013-09-30 15:20:16,428 <sample.py[InputHandler]:DEBUG> Starting handler: message/234479244
    2013-09-30 15:20:16,428 <sample.py[OutputHandler]:DEBUG> Received command: %%<message:234479288:false:engine.timer::time=1095112796
    2013-09-30 15:20:16,428 <sample.py[OutputHandler]:DEBUG> Sending: %%<message:234479288:false:engine.timer::time=1095112796
    2013-09-30 15:20:16,428 <sample.py[InputHandler]:DEBUG> Received command: %%<uninstall:50:test:false
    2013-09-30 15:20:16,429 <sample.py[message/234479244]:DEBUG> Processing command: %%>message:234479244:1095112797:engine.timer::time=1095112797
    2013-09-30 15:20:16,429 <sample.py[InputHandler]:DEBUG> Removed finished thread: message/234479288
    2013-09-30 15:20:16,429 <sample.py[message/234479244]:DEBUG> No action defined, replying without processing
    2013-09-30 15:20:16,429 <sample.py[InputHandler]:DEBUG> Starting handler: uninstall/test
    2013-09-30 15:20:16,430 <sample.py[OutputHandler]:DEBUG> Received command: %%<message:234479244:false:engine.timer::time=1095112797
    2013-09-30 15:20:16,430 <sample.py[uninstall/test]:DEBUG> Processing command: %%<uninstall:50:test:false
    2013-09-30 15:20:16,430 <sample.py[InputHandler]:DEBUG> Received command: %%<uninstall:100:engine.timer:true
    2013-09-30 15:20:16,430 <sample.py[OutputHandler]:DEBUG> Sending: %%<message:234479244:false:engine.timer::time=1095112797
    2013-09-30 15:20:16,430 <sample.py[uninstall/test]:ERROR> Error executing command: %%>uninstall:test
    2013-09-30 15:20:16,430 <sample.py[InputHandler]:DEBUG> Removed finished thread: message/234479244
    2013-09-30 15:20:16,431 <sample.py[InputHandler]:DEBUG> Starting handler: uninstall/engine.timer
    2013-09-30 15:20:16,431 <sample.py[uninstall/engine.timer]:DEBUG> Processing command: %%<uninstall:100:engine.timer:true
    2013-09-30 15:20:16,432 <sample.py[InputHandler]:DEBUG> Received command: %%<uninstall:100:engine.timer:true
    2013-09-30 15:20:16,432 <sample.py[uninstall/engine.timer]:DEBUG> Command executed successfully: %%>uninstall:engine.timer
    2013-09-30 15:20:16,432 <sample.py[InputHandler]:DEBUG> Removed finished thread: uninstall/test
    2013-09-30 15:20:16,432 <sample.py[InputHandler]:DEBUG> Starting handler: uninstall/engine.timer
    2013-09-30 15:20:16,432 <sample.py[uninstall/engine.timer]:DEBUG> Processing command: %%<uninstall:100:engine.timer:true
    2013-09-30 15:20:16,433 <sample.py[InputHandler]:DEBUG> Received command: %%>message:234479244:1095112797:engine.test:false:testing=true
    2013-09-30 15:20:16,433 <sample.py[uninstall/engine.timer]:ERROR> ID not found on command queue: 'uninstall/engine.timer'
    2013-09-30 15:20:16,433 <sample.py[InputHandler]:DEBUG> Removed finished thread: uninstall/engine.timer
    2013-09-30 15:20:16,433 <sample.py[InputHandler]:DEBUG> Starting handler: message/234479244
    2013-09-30 15:20:16,433 <sample.py[InputHandler]:DEBUG> Received command: %%<unwatch:call.route:true
    2013-09-30 15:20:16,434 <sample.py[message/234479244]:DEBUG> Processing command: %%>message:234479244:1095112797:engine.test:false:testing=true
    2013-09-30 15:20:16,434 <sample.py[InputHandler]:DEBUG> Removed finished thread: uninstall/engine.timer
    2013-09-30 15:20:16,434 <sample.py[message/234479244]:DEBUG> No action defined, replying without processing
    2013-09-30 15:20:16,434 <sample.py[InputHandler]:DEBUG> Starting handler: unwatch/call.route
    2013-09-30 15:20:16,434 <sample.py[unwatch/call.route]:DEBUG> Processing command: %%<unwatch:call.route:true
    2013-09-30 15:20:16,435 <sample.py[OutputHandler]:DEBUG> Received command: %%<message:234479244:false:engine.test:false:testing=true
    2013-09-30 15:20:16,435 <sample.py[unwatch/call.route]:DEBUG> Command executed successfully: %%>unwatch:call.route
    2013-09-30 15:20:16,435 <sample.py[OutputHandler]:DEBUG> Sending: %%<message:234479244:false:engine.test:false:testing=true
    2013-09-30 15:20:16,435 <sample.py[InputHandler]:DEBUG> Received command: Error in:%%>watch:call.route
    2013-09-30 15:20:16,436 <sample.py[InputHandler]:DEBUG> Removed finished thread: message/234479244
    2013-09-30 15:20:16,436 <sample.py[InputHandler]:DEBUG> Starting handler: error/%%>watch:call.route
    2013-09-30 15:20:16,436 <sample.py[error/%%>watch:call.route]:DEBUG> Processing command: Error in:%%>watch:call.route
    2013-09-30 15:20:16,436 <sample.py[InputHandler]:DEBUG> Received command: None
    2013-09-30 15:20:16,436 <sample.py[error/%%>watch:call.route]:ERROR> Invalid command: %%>watch:call.route
    2013-09-30 15:20:16,436 <sample.py[InputHandler]:DEBUG> Removed finished thread: unwatch/call.route
    2013-09-30 15:20:16,537 <sample.py[InputHandler]:DEBUG> Removed finished thread: error/%%>watch:call.route
    2013-09-30 15:20:16,537 <sample.py[InputHandler]:INFO> Finished
    2013-09-30 15:20:16,538 <sample.py[MainThread]:DEBUG> Shutting down output queue
    2013-09-30 15:20:16,538 <sample.py[MainThread]:DEBUG> Waiting for output queue handler
    2013-09-30 15:20:16,538 <sample.py[OutputHandler]:DEBUG> Received command: None
    2013-09-30 15:20:16,538 <sample.py[OutputHandler]:INFO> Finished


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
