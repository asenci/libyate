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
