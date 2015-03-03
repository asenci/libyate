"""
Test cases for libyate.cmd
"""

import libyate.engine
import libyate.type

from datetime import datetime
from unittest import TestCase


#
# Meta classes
#

# noinspection PyDocstring,PyUnresolvedReferences
class CmdCaseMeta(type):
    """Meta class for Command test cases"""

    def __new__(mcs, name, bases, attrs):
        # Get command class
        cmd_class = attrs.get('cmd_class')

        # Get strings
        strings = attrs.get('strings', ())

        if cmd_class is None:
            attrs['test_cmd_abstract_raise'] = \
                lambda self: \
                self.assertRaises(TypeError, libyate.engine.Command)

        for n, (s, d) in enumerate(strings):
            def test_cmd_from_string(cmd_obj, string):
                return lambda self: self.assertEqual(str(cmd_obj), string)

            def test_cmd_from_repr(cmd_obj):
                def test(self):
                    import datetime
                    import libyate.engine
                    import libyate.type

                    self.assertEqual(eval(repr(cmd_obj)), cmd_obj)

                return test

            def test_cmd_from_kwargs(cmd_obj, kwargs):
                return lambda self: self.assertEqual(
                    self.cmd_class(**kwargs), cmd_obj)

            def test_cmd_desc(cmd_obj, key, value):
                return lambda self: self.assertEqual(
                    getattr(cmd_obj, key), value)

            cmd = libyate.engine.from_string(s)

            attrs['test_cmd_from_string_%s' % n] = test_cmd_from_string(cmd, s)
            attrs['test_cmd_from_repr_%s' % n] = test_cmd_from_repr(cmd)

            if cmd_class is not None and d is not None:
                attrs['test_cmd_from_kwargs_%s' % n] = \
                    test_cmd_from_kwargs(cmd, d)

                for k, v in d.items():
                    attrs['test_cmd_%s_desc_%s' % (n, k)] = \
                        test_cmd_desc(cmd, k, v)

        return super(CmdCaseMeta, mcs).__new__(mcs, name, bases, attrs)


#
# Test cases
#

class TestYateCmd(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = None
    strings = ()

    def test_cmd_from_string_raise(self):
        self.assertRaises(NotImplementedError,
                          libyate.engine.from_string,
                          '%%>invalid_method:false')

    def test_cmd_no_keyword_raise(self):
        # noinspection PyDocstring
        class C(libyate.engine.Command):
            def __init__(self):
                super(C, self).__init__()

        cmd = C()
        self.assertRaises(NotImplementedError, str, cmd)

    def test_cmd_neq(self):
        c1 = libyate.engine.from_string('%%>connect:test')
        c2 = libyate.engine.from_string('%%>connect:test2')
        self.assertNotEqual(c1, c2)

    def test_cmd_repr(self):
        self.assertEqual(repr(
            libyate.engine.from_string('%%>message:myapp55251%%:1095112794:app'
                                       '.job%z::path=/bin%z/usr/bin:job=cleanu'
                                       'p:done=75%%')),
                         "libyate.engine.Message('myapp55251%', datetime.datet"
                         "ime(2004, 9, 13, 21, 59, 54), 'app.job:', None, liby"
                         "ate.type.OrderedDict((('path', '/bin:/usr/bin'), ('j"
                         "ob', 'cleanup'), ('done', '75%'))))")

    def test_cmd_unicode(self):
        self.assertTrue(isinstance(unicode(
            libyate.engine.from_string('%%>connect:test')), unicode))


class TestYateCmdConnect(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.Connect
    strings = (
        ('%%>connect:test::', dict(role='test')),
        ('%%>connect:test:1234:', dict(role='test', id='1234')),
        ('%%>connect:test:any_id:audio',
         dict(role='test', id='any_id', type='audio')),
        ('%%>connect:test%%:any_id%z:audio%}',
         dict(role='test%', id='any_id:', type='audio=')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdError(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.Error
    strings = (
        ('Error in:%%>install::engine.timer',
         dict(original='%%>install::engine.timer')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdInstall(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.Install
    strings = (
        ('%%>install::test::', dict(name='test')),
        ('%%>install:50:test::', dict(priority=50, name='test')),
        ('%%>install:50:test:filter:',
         dict(priority=50, name='test', filter_name='filter')),
        ('%%>install:50:test:filter:value',
         dict(priority=50, name='test', filter_name='filter',
              filter_value='value')),
        ('%%>install:50:test%%:filter%z:value%}',
         dict(priority=50, name='test%', filter_name='filter:',
              filter_value='value=')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, name='')
        self.assertRaises(ValueError, self.cmd_class, priority='ok')


class TestYateCmdInstallReply(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.InstallReply
    strings = (
        ('%%<install:100:test:true',
         dict(priority=100, name='test', success=True)),
        ('%%<install:100:test:false',
         dict(priority=100, name='test', success=False)),
        ('%%<install:100:test%%:false',
         dict(priority=100, name='test%', success=False)),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, priority=100, name='')
        self.assertRaises(ValueError, self.cmd_class, priority=100,
                          name='test', success='')
        self.assertRaises(ValueError, self.cmd_class, priority='ok',
                          name='test', success=True)
        self.assertRaises(ValueError, self.cmd_class, priority=100,
                          name='test', success='no')


class TestYateCmdMessage(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.Message
    strings = (
        ('%%>message:234479288:1095112796:engine.timer::',
         dict(id='234479288', time=datetime.utcfromtimestamp(1095112796),
              name='engine.timer')),
        ('%%>message:234479288:1095112796:engine.timer:ok:',
         dict(id='234479288', time=datetime.utcfromtimestamp(1095112796),
              name='engine.timer', retvalue='ok')),
        ('%%>message:234479288:1095112796:engine.timer:ok:time=1095112796',
         dict(id='234479288', time=datetime.utcfromtimestamp(1095112796),
              name='engine.timer', retvalue='ok',
              kvp=libyate.type.OrderedDict((('time', '1095112796'),)))),
        ('%%>message:234479288:1095112796:engine.timer::time=1095112796',
         dict(id='234479288', time=datetime.utcfromtimestamp(1095112796),
              name='engine.timer',
              kvp=libyate.type.OrderedDict((('time', '1095112796'),)))),
        ('%%>message:myapp55251%%:1095112794:app.job%z::job=cleanup:job.done='
         '75%%:path=/bin%z/usr/bin%z',
         dict(id='myapp55251%', time=datetime.utcfromtimestamp(1095112794),
              name='app.job:',
              kvp=libyate.type.OrderedDict(
                  (('job', 'cleanup'), ('job.done', '75%'),
                   ('path', '/bin:/usr/bin:'))))),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, time='')
        self.assertRaises(ValueError, self.cmd_class, name='')
        self.assertRaises(ValueError, self.cmd_class, time='now')

    def test_cmd_reply(self):
        self.assertTrue(isinstance(self.cmd_class().reply(),
                                   libyate.engine.MessageReply))


class TestYateCmdMessageReply(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.MessageReply
    strings = (
        ('%%<message:234479208:false:::',
         dict(id='234479208', processed=False)),
        ('%%<message:234479208:false:engine.timer::',
         dict(id='234479208', processed=False, name='engine.timer')),
        ('%%<message:234479208:false:engine.timer:ok:',
         dict(id='234479208', processed=False, name='engine.timer',
              retvalue='ok')),
        ('%%<message:234479208:false:engine.timer:ok:time=1095112796',
         dict(id='234479208', processed=False, name='engine.timer',
              retvalue='ok',
              kvp=libyate.type.OrderedDict((('time', '1095112796'),)))),
        ('%%<message:234479208:false::ok:time=1095112796',
         dict(id='234479208', processed=False, retvalue='ok',
              kvp=libyate.type.OrderedDict((('time', '1095112796'),)))),
        ('%%<message:234479208:false:::time=1095112796',
         dict(id='234479208', processed=False,
              kvp=libyate.type.OrderedDict((('time', '1095112796'),)))),
        ('%%<message:234479208:false:engine.timer::time=1095112796',
         dict(id='234479208', processed=False, name='engine.timer',
              kvp=libyate.type.OrderedDict((('time', '1095112796'),)))),
        ('%%<message:myapp55251%%:true:app.job%z:Restart required%}:path='
         '/bin%z/usr/bin%z/usr/local/bin',
         dict(id='myapp55251%', processed=True, name='app.job:',
              retvalue='Restart required=',
              kvp=libyate.type.OrderedDict(
                  (('path', '/bin:/usr/bin:/usr/local/bin'),)))),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, processed='')
        self.assertRaises(ValueError, self.cmd_class, processed='ok')


class TestYateCmdOutput(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.Output
    strings = (
        ('%%>output:arbitrary unescaped string%%',
         dict(output='arbitrary unescaped string%%')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdSetLocal(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.SetLocal
    strings = (
        ('%%>setlocal:test:', dict(name='test')),
        ('%%>setlocal:test:true', dict(name='test', value='true')),
        ('%%>setlocal:test%z:true%%', dict(name='test:', value='true%')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdSetLocalReply(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.SetLocalReply
    strings = (
        ('%%<setlocal:test:true:true',
         dict(name='test', value='true', success=True)),
        ('%%<setlocal:test%%:true%z:true',
         dict(name='test%', value='true:', success=True)),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase, success='true')
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, name='test')
        self.assertRaises(ValueError, self.cmd_class, name='test',
                          value='true')
        self.assertRaises(ValueError, self.cmd_class, name='test',
                          value='true', success='ok')


class TestYateCmdUnInstall(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.UnInstall
    strings = (
        ('%%>uninstall:test', dict(name='test')),
        ('%%>uninstall:test%%', dict(name='test%')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdUnInstallReply(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.UnInstallReply
    strings = (
        ('%%<uninstall:100:test:true',
         dict(priority=100, name='test', success=True)),
        ('%%<uninstall:100:test:false',
         dict(priority=100, name='test', success=False)),
        ('%%<uninstall:100:test%%:false',
         dict(priority=100, name='test%', success=False)),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, priority=100, name='')
        self.assertRaises(ValueError, self.cmd_class, priority=100,
                          name='test', success='')
        self.assertRaises(ValueError, self.cmd_class, priority='ok',
                          name='test', success=True)
        self.assertRaises(ValueError, self.cmd_class, priority=100,
                          name='test', success='no')


class TestYateCmdUnWatch(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.UnWatch
    strings = (
        ('%%>unwatch:test', dict(name='test')),
        ('%%>unwatch:test%%', dict(name='test%')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdUnWatchReply(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.UnWatchReply
    strings = (
        ('%%<unwatch:test:true', dict(name='test', success=True)),
        ('%%<unwatch:test:false', dict(name='test', success=False)),
        ('%%<unwatch:test%%:false', dict(name='test%', success=False)),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, name='test', success='')
        self.assertRaises(ValueError, self.cmd_class, name='test',
                          success='no')


class TestYateCmdWatch(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.Watch
    strings = (
        ('%%>watch:test', dict(name='test')),
        ('%%>watch:test%%', dict(name='test%')),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')


class TestYateCmdWatchReply(TestCase):
    __metaclass__ = CmdCaseMeta

    cmd_class = libyate.engine.WatchReply
    strings = (
        ('%%<watch:test:true', dict(name='test', success=True)),
        ('%%<watch:test:false', dict(name='test', success=False)),
        ('%%<watch:test%%:false', dict(name='test%', success=False)),
    )

    def test_cmd_from_kwargs_raise(self):
        self.assertRaises(TypeError, self.cmd_class, TestCase)
        self.assertRaises(ValueError, self.cmd_class, '')
        self.assertRaises(ValueError, self.cmd_class, name='test', success='')
        self.assertRaises(ValueError, self.cmd_class, name='test',
                          success='no')
