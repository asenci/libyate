# Python library for developing Yate external modules
A more "pythonic" aproach to Yate.

## Sample application:

    :::python
    #!/usr/bin/env python
    import libyate


    class my_app(libyate.YateExtModule):
        def on_start(self):
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

        def on_stop(self):
            pass


    from optparse import OptionParser

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
    %%>message:234479244:1095112797:engine.test:false
    %%<unwatch:call.route:true
    Error in:%%>watch:call.route
    %%>teste:234479244:1095112797:engine.test:false

Expected output:

    :::text
    $ python sample.py -d < sample_reply.txt >/dev/null
    1377213607.465684 <sample.py:DEBUG> Loading module
    1377213607.466423 <sample.py:DEBUG> Sending: %%>setlocal:testing:true
    1377213607.466641 <sample.py:DEBUG> Sending: %%>install:50:test
    1377213607.466892 <sample.py:DEBUG> Sending: %%>install::engine.timer
    1377213607.467152 <sample.py:DEBUG> Sending: %%>watch:call.route
    1377213607.467480 <sample.py:DEBUG> Sending: %%>message:myapp55251:1377213607:app.job::path=/bin%z/usr/bin:job=cleanup:done=75%%
    1377213607.467843 <sample.py:DEBUG> Sending: %%>uninstall:test
    1377213607.468034 <sample.py:DEBUG> Sending: %%>uninstall:engine.timer
    1377213607.468208 <sample.py:DEBUG> Sending: %%>unwatch:call.route
    1377213607.468346 <sample.py:DEBUG> Entering main loop
    1377213607.468448 <sample.py:DEBUG> Queue size: 8
    1377213607.468573 <sample.py:DEBUG> Received: %%<setlocal:testing:true:true
    1377213607.468814 <sample.py:DEBUG> Command executed successfully: %%>setlocal:testing:true
    1377213607.468883 <sample.py:DEBUG> Queue size: 7
    1377213607.468981 <sample.py:DEBUG> Received: %%<install:50:test:true
    1377213607.469207 <sample.py:DEBUG> Command executed successfully: %%>install:50:test
    1377213607.469287 <sample.py:DEBUG> Queue size: 6
    1377213607.469390 <sample.py:DEBUG> Received: %%<install:100:engine.timer:true
    1377213607.469637 <sample.py:DEBUG> Command executed successfully: %%>install::engine.timer
    1377213607.469714 <sample.py:DEBUG> Queue size: 5
    1377213607.469811 <sample.py:DEBUG> Received: %%<message:myapp55251:true:app.job:Restart required:path=/bin%z/usr/bin%z/usr/local/bin
    1377213607.470118 <sample.py:DEBUG> Command executed successfully: %%>message:myapp55251:1377213607:app.job::path=/bin%z/usr/bin:job=cleanup:done=75%%
    1377213607.470197 <sample.py:DEBUG> Queue size: 4
    1377213607.470291 <sample.py:DEBUG> Received: %%>message:234479208:1095112795:engine.timer::time=1095112795
    1377213607.470554 <sample.py:DEBUG> Sending: %%<message:234479208:false:engine.timer::time=1095112795
    1377213607.470718 <sample.py:DEBUG> Queue size: 4
    1377213607.470795 <sample.py:DEBUG> Received: %%>message:234479288:1095112796:engine.timer::time=1095112796
    1377213607.471056 <sample.py:DEBUG> Sending: %%<message:234479288:false:engine.timer::time=1095112796
    1377213607.471212 <sample.py:DEBUG> Queue size: 4
    1377213607.471288 <sample.py:DEBUG> Received: %%>message:234479244:1095112797:engine.timer::time=1095112797
    1377213607.471546 <sample.py:DEBUG> Sending: %%<message:234479244:false:engine.timer::time=1095112797
    1377213607.471701 <sample.py:DEBUG> Queue size: 4
    1377213607.471777 <sample.py:DEBUG> Received: %%<uninstall:50:test:false
    1377213607.471945 <sample.py:ERROR> Error executing command: %%>uninstall:test
    1377213607.472017 <sample.py:DEBUG> Queue size: 3
    1377213607.472110 <sample.py:DEBUG> Received: %%<uninstall:100:engine.timer:true
    1377213607.472301 <sample.py:DEBUG> Command executed successfully: %%>uninstall:engine.timer
    1377213607.472379 <sample.py:DEBUG> Queue size: 2
    1377213607.472475 <sample.py:DEBUG> Received: %%<uninstall:100:engine.timer:true
    1377213607.472620 <sample.py:DEBUG> Queue size: 2
    1377213607.472696 <sample.py:DEBUG> Received: %%>message:234479244:1095112797:engine.test:false
    1377213607.472931 <sample.py:DEBUG> Sending: %%<message:234479244:false:engine.test:false
    1377213607.473076 <sample.py:DEBUG> Queue size: 2
    1377213607.473153 <sample.py:DEBUG> Received: %%<unwatch:call.route:true
    1377213607.473324 <sample.py:DEBUG> Command executed successfully: %%>unwatch:call.route
    1377213607.473395 <sample.py:DEBUG> Queue size: 1
    1377213607.473488 <sample.py:DEBUG> Received: Error in:%%>watch:call.route
    1377213607.473612 <sample.py:ERROR> Invalid command: %%>watch:call.route
    1377213607.473745 <sample.py:DEBUG> Queue size: 0
    1377213607.473850 <sample.py:DEBUG> Received: %%>teste:234479244:1095112797:engine.test:false
    Traceback (most recent call last):
        (...)
    NotImplementedError: Command method "%%>teste" not implemented

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
