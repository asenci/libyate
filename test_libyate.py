from datetime import datetime
from unittest import TestCase

from libyate import YateCmd


class TestYateCmd(TestCase):

    def test_cmd_from_string(self):
        list = [
            '%%>install:50:test',
            '%%<install:50:test:true',
            '%%>install::engine.timer',
            '%%<install:100:engine.timer:true',
            '%%>message:myapp55251:1095112794:app.job::job=cleanup',
            '%%>message:myapp55251:1095112794:app.job::done=75%%',
            '%%>message:myapp55251:1095112794:app.job::path=/bin%Z/usr/bin',
            '%%>message:234479208:1095112795:engine.timer::time=1095112795',
            '%%<message:myapp55251:true:app.job:Restart required:path=/bin%Z/usr/bin%Z/usr/local/bin',
            '%%<message:234479208:false:engine.timer::time=1095112795',
            '%%>uninstall:test',
            '%%<uninstall:50:test:true',
            '%%>message:234479288:1095112796:engine.timer::time=1095112796',
            '%%<message:234479288:false:engine.timer::time=1095112796',
            '%%<message:234479288:false:engine.timer::extra=yes',
            '%%>message:234479244:1095112797:engine.timer::time=1095112797',
        ]
        for s in list:
            c = YateCmd(s)
            self.assertEqual(s, str(c))

    def test_cmd_from_cmd(self):
        s = '%%<message:234479208:false:engine.timer::time=1095112795'
        c1 = YateCmd(s)
        c2 = YateCmd(c1)

        self.assertEqual(str(c1), str(c2))

    def test_cmd_from_kwargs(self):
        s = '%%<message:234479208:false:engine.timer::time=1095112795'
        kwargs = {
            'method': '%%<message',
            'id': '234479208',
            'processed': False,
            'name': 'engine.timer',
            'retval': '',
            'kvp': {
                'time': '1095112795'
            }

        }

        c = YateCmd(**kwargs)

        self.assertEqual(s, str(c))

    def test_cmd_reply_ok(self):
        sc = '%%>install:50:test'
        sr = '%%<install:50:test:true'
        c = YateCmd(sc)
        r = YateCmd(sr)

        self.assertTrue(c(r))

    def test_cmd_reply_nok(self):
        sc = '%%>install:50:test'
        sr = '%%<install:50:test:false'
        c = YateCmd(sc)
        r = YateCmd(sr)

        self.assertFalse(c(r))

    def test_cmd_params(self):
        s='%%>message:myapp55251:1095112794:app.job::job=cleanup:done=75%%:path=/bin%z/usr/bin'
        c = YateCmd(s)

        self.assertEqual(c.__method__, '%%>message')
        self.assertEqual(c.id, 'myapp55251')
        self.assertEqual(c.time, datetime.fromtimestamp(1095112794))
        self.assertEqual(c.name, 'app.job')
        self.assertEqual(c.retvalue, '')
        self.assertEqual(c.kvp['job'], 'cleanup')
        self.assertEqual(c.kvp['done'], '75%')
        self.assertEqual(c.kvp['path'], '/bin:/usr/bin')
