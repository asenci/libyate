#!/usr/bin/env python
import libyate


class my_app(libyate.YateExtModule):
    def on_start(self):
        self.send(libyate.YateCmdSetLocal(
            name='testing', value='true'))
        self.send(libyate.YateCmdInstall(
            name='test', priority=50))
        self.send(libyate.YateCmdInstall(
            name='engine.timer'))
        self.send(libyate.YateCmdWatch(
            name='call.route'))
        self.send(libyate.YateCmdMessage(
            name='app.job', id='myapp55251', kvp={
                'job': 'cleanup', 'done': '75%', 'path': '/bin:/usr/bin'
            }))
        self.send(libyate.YateCmdUnInstall(
            name='test'))
        self.send(libyate.YateCmdUnInstall(
            name='engine.timer'))
        self.send(libyate.YateCmdUnWatch(
            name='call.route'))

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
