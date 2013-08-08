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


from optparse import OptionParser

parser = OptionParser()
parser.add_option('-d', '--debug', action='store_true',
                  help='increase logging verbosity')
parser.add_option('-q', '--quiet', action='store_true',
                  help='reduce the logging verbosity')
parser.add_option('-n', '--name', default=__file__,
                  help='name used for logging')

myapp(**vars(parser.parse_args()[0])).run()
