#!/usr/bin/env python
"""
Sample application to test libyate
"""

import logging
import optparse

import libyate.app


# noinspection PyDocstring,PyUnusedLocal
class MyApp(libyate.app.Script):
    def run(self):
        # Query engine version
        self.set_local('engine.version')

        # Install handler for "call.route"
        self.install('call.route', priority=50, handler=self.call_route)

        # Install watcher for "engine.timer"
        self.watch('engine.timer', handler=self.timer)

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

    MyApp('sample.py').start()
