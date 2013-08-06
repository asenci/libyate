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
