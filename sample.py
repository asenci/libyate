"""
Sample application to test libyate
"""
import libyate


class MyApp(libyate.YateExtModule):
    def on_start(self):
        self.set_local('testing', 'true')
        self.set_local('engine.version')
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


if __name__ == '__main__':
    import logging
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true', default=False,
                      help='increase logging verbosity')
    parser.add_option('-q', '--quiet', action='store_true', default=False,
                      help='reduce the logging verbosity')
    parser.add_option('-n', '--name',
                      help='name used for logging')

    options, _ = parser.parse_args()

    log_format = \
        '%(asctime)s <%(name)s[%(threadName)s]:%(levelname)s> %(message)s'

    logging.basicConfig(**{
        'level': (logging.DEBUG if options.debug else
                  logging.WARN if options.quiet else
                  logging.INFO),
        'format': log_format,
    })

    MyApp(options.name).run()
