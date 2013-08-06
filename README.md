# Python library for developing Yate IVR's
A more "pythonic" aproach to Yate.

## Sample application:

    :::python
    import libyate

    myapp = libyate.YateScript(debug=False, quiet=False)

    myapp.write(myapp.new_setlocal('testing', 'true'))
    myapp.write(myapp.new_install('test', 50))
    myapp.write(myapp.new_install('engine.timer'))
    myapp.write(myapp.new_watch('call.route'))
    myapp.write(myapp.new_watch('call.route'))
    myapp.write(myapp.new_message('app.job', id='myapp55251',
                                  job='cleanup', done='75%',
                                  path='/bin:/usr/bin'))
    myapp.write(myapp.new_uninstall('test'))
    myapp.write(myapp.new_uninstall('engine.timer'))
    myapp.write(myapp.new_unwatch('call.route'))

    myapp.run(name=__file__)

Can be tested passing this lines into stdin:

    :::text
    %%<setlocal:testing:true:true
    %%<install:50:test:true
    %%<install:100:engine.timer:true
    %%<watch:call.route:true
    %%<message:myapp55251:true:app.job:Restart required:path=/bin%Z/usr/bin%Z/usr/local/bin
    %%>message:234479208:1095112795:engine.timer::time=1095112795
    %%>message:234479288:1095112796:engine.timer::time=1095112796
    %%>message:234479244:1095112797:engine.timer::time=1095112797
    %%<uninstall:50:test:false
    %%<uninstall:100:engine.timer:true
    %%>message:234479244:1095112797:engine.test:false
    %%<unwatch:call.route:true
    %%>teste:234479244:1095112797:engine.test:false
    Error in:test %% string !

Expected output:

    :::text
    $ python sample.py < sample_reply.txt >/dev/null
    Loading script "sample.py"
    Parameter changed successfully: testing=true
    Message handler installed successfully for: test
    Message handler installed successfully for: engine.timer
    Message watcher installed successfully for: call.route
    Processing completed on message "myapp55251"
    Error uninstalling message handler for: test
    Message handler uninstalled successfully for: engine.timer
    Message watcher uninstalled successfully for: call.route
    Method "%%>teste" not implemented
    Invalid command: test % string !
    End of stream

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
