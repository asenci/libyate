# Python library for developing Yate IVR's
A more "pythonic" aproach to Yate.

## Sample application:

    :::python
    import libyate


    class myapp(libyate.YateExtModule):
        def on_start(self):
            self.send(libyate.YateCmdSetLocal('testing', 'true'))
            self.send(libyate.YateCmdInstall('test', 50))
            self.send(libyate.YateCmdInstall('engine.timer'))
            self.send(libyate.YateCmdWatch('call.route'))
            self.send(libyate.YateCmdMessage('app.job',
                                                    id='myapp55251',
                                                    extras={
                                                        'job': 'cleanup',
                                                        'done': '75%',
                                                        'path': '/bin:/usr/bin'
                                                    }))
            self.send(libyate.YateCmdUnInstall('test'))
            self.send(libyate.YateCmdUnInstall('engine.timer'))
            self.send(libyate.YateCmdUnWatch('call.route'))

        def on_stop(self):
            pass


    from argparse import ArgumentParser

    parser = ArgumentParser(
        description='Sample external module for Yate telephony engine')

    parser.add_argument('-d', '--debug', action='store_true',
                        help='increase logging verbosity')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='reduce the logging verbosity')
    parser.add_argument('-n', '--name', default=__file__,
                        help='name used for logging')


    myapp(**vars(parser.parse_args())).run()

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
    $ python sample.py < sample_reply.txt >/dev/null
    1376003543.481805 <sample.py:INFO> Loading module
    1376003543.484129 <sample.py:ERROR> Error executing command: %%>uninstall:test
    1376003543.484354 <sample.py:ERROR> Invalid reply: %%<uninstall:100:engine.timer:true
    1376003543.484662 <sample.py:ERROR> Invalid command: %%>watch:call.route
    1376003543.484799 <sample.py:ERROR> Method "%%>teste" not implemented


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
