"""
Test cases for libyate.type
"""

import libyate.type
from unittest import TestCase


#
# Meta classes
#

# noinspection PyDocstring
class TypeCaseMeta(type):
    """Meta class for Command test cases"""

    def __new__(mcs, name, bases, attrs):
        # Get command class
        type_class = attrs.get('type_class')

        # Get strings
        values = attrs.get('values', ())

        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = type_class(blank=True)
            not_blank = type_class()

        o = C()

        for n, (v, r, s) in enumerate(values):
            def test_value_repr(obj, val, rep, st):
                def test(self):
                    setattr(obj, 'attr', val)
                    self.assertEqual(rep, obj.__dict__['attr'])
                    self.assertEqual(st, C.attr.to_string(o))

                return test

            def test_blank(obj):
                def test(self):
                    self.assertRaises(
                        ValueError, setattr, obj, 'not_blank', None)

                return test

            attrs['test_value_repr_%s' % n] = test_value_repr(o, v, r, s)
            attrs['test_blank'] = test_blank(o)

        return super(TypeCaseMeta, mcs).__new__(mcs, name, bases, attrs)


#
# Test cases
#

class TestBaseType(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.Descriptor
    values = (
        ('', '', ''),
        ('a', 'a', 'a'),
        (('a',), ('a',), "('a',)"),
        (0, 0, '0'),
        (None, None, ''),
        (True, True, 'true'),
        (u'a', u'a', u'a'),
    )

    def test_repr(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        self.assertEqual('<libyate.type.Descriptor "attr">', repr(C.attr))

    def test_delete(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.Descriptor()

        o = C()
        self.assertTrue('attr' not in o.__dict__)

        o.attr = 'a'
        self.assertTrue('attr' in o.__dict__)

        del o.attr
        self.assertTrue('attr' not in o.__dict__)


class TestBoolean(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.Boolean
    values = (
        ('', None, ''),
        ('false', False, 'false'),
        ('true', True, 'true'),
        (False, False, 'false'),
        (None, None, ''),
        (True, True, 'true'),
    )

    def test_raises(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', 'tru')
        self.assertRaises(TypeError, setattr, o, 'attr', 0)


class TestDateTime(TestCase):
    from datetime import datetime

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.DateTime
    values = (
        ('', None, ''),
        ('1095112796', datetime.utcfromtimestamp(1095112796), '1095112796'),
        (1095112796, datetime.utcfromtimestamp(1095112796), '1095112796'),
        (datetime.utcfromtimestamp(1095112796),
         datetime.utcfromtimestamp(1095112796), '1095112796'),
        (None, None, ''),
    )

    def test_raises(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', 'a')
        self.assertRaises(TypeError, setattr, o, 'attr', True)


class TestInteger(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.Integer
    values = (
        ('', None, ''),
        ('0', 0, '0'),
        (0, 0, '0'),
        (None, None, ''),
    )

    def test_raises(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', 'a')
        self.assertRaises(TypeError, setattr, o, 'attr', True)


class TestKeyValueList(TestCase):
    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.KeyValueList
    values = (
        ('', None, ''),
        ('job=cleanup:job.done=75%%:path=/bin%z/usr/bin%z',
         libyate.type.OrderedDict(
             (('job', 'cleanup'), ('job.done', '75%'),
              ('path', '/bin:/usr/bin:'))),
         'job=cleanup:job.done=75%%:path=/bin%z/usr/bin%z'),
        ('time', libyate.type.OrderedDict((('time', ''),)), 'time'),
        ('time=1095112796', libyate.type.OrderedDict(
            (('time', '1095112796'),)), 'time=1095112796'),
        ((('job', 'cleanup'), ('job.done', '75%'), ('path', '/bin:/usr/bin:')),
         libyate.type.OrderedDict(
             (('job', 'cleanup'), ('job.done', '75%'),
              ('path', '/bin:/usr/bin:'))),
         'job=cleanup:job.done=75%%:path=/bin%z/usr/bin%z'),
        ((('time', '1095112796'),), libyate.type.OrderedDict(
            (('time', '1095112796'),)), 'time=1095112796'),
        ((('time', None),), libyate.type.OrderedDict(
            (('time', None),)), 'time'),
        ([['time', '1095112796'], ], libyate.type.OrderedDict(
            (('time', '1095112796'),)), 'time=1095112796'),
        (None, None, ''),
        ({'done': True}, libyate.type.OrderedDict(
            (('done', True),)), 'done=true'),
        ({'time': '1095112796'}, libyate.type.OrderedDict(
            (('time', '1095112796'),)), 'time=1095112796'),
        ({'time': 1095112796}, libyate.type.OrderedDict(
            (('time', 1095112796),)), 'time=1095112796'),
    )

    def test_raises(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', '=')
        self.assertRaises(ValueError, setattr, o, 'attr', '=a')
        self.assertRaises(TypeError, setattr, o, 'attr', True)

    # noinspection PyUnresolvedReferences
    def test_values(self):
        # noinspection PyDocstring
        class KVP(object):
            __metaclass__ = libyate.type.DescriptorMeta

            kvp = libyate.type.KeyValueList()

        kvp = KVP()
        kvp.kvp = 'job=cleanup:job.done=75%%:path=/bin%z/usr/bin%z'

        self.assertEqual(libyate.type.OrderedDict(
            (('job', 'cleanup'), ('job.done', '75%'),
             ('path', '/bin:/usr/bin:'))), kvp.__dict__['kvp'])
        self.assertEqual('cleanup', kvp.kvp['job'])
        self.assertEqual('75%', kvp.kvp['job.done'])
        self.assertEqual('/bin:/usr/bin:', kvp.kvp['path'])


class TestString(TestCase):
    from datetime import datetime

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.String
    values = (
        ('', None, ''),
        ('a', 'a', 'a'),
        (0, '0', '0'),
        (None, None, ''),
        (True, 'true', 'true'),
        (u'a', u'a', u'a'),
        (datetime.utcfromtimestamp(1095112796), '1095112796', '1095112796')
    )

    def test_raises(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', '')
        self.assertRaises(TypeError, setattr, o, 'attr', ('a',))

    def test_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')

    def test_max_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(max_length=3)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'abc')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')

    def test_min_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(min_length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')

    def test_max_min_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(min_length=2, max_length=4)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'a')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcde')


class TestEncodedString(TestCase):

    __metaclass__ = TypeCaseMeta

    # noinspection PyDocstring,PyPep8Naming
    class type_class(libyate.type.String):
        encoded = True

    values = (
        ('', None, ''),
        ('a', 'a', 'a'),
        (u'a', u'a', u'a'),
        ('%', '%', '%%'),
        (0, '0', '0'),
        (None, None, ''),
        (True, 'true', 'true'),
    )

    def test_raises(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', '')
        self.assertRaises(TypeError, setattr, o, 'attr', ('a',))

    def test_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'ab%')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')
        self.assertRaises(ValueError, setattr, o, 'attr', 'a%')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abc%')

    def test_max_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(max_length=3)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'a%')
        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'ab%')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abc%')

    def test_min_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(min_length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'ab%')
        setattr(o, 'attr', 'abcd')
        setattr(o, 'attr', 'abc%')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')
        self.assertRaises(ValueError, setattr, o, 'attr', 'a%')

    def test_max_min_length(self):
        # noinspection PyDocstring
        class C(object):
            __metaclass__ = libyate.type.DescriptorMeta

            attr = libyate.type.String(min_length=2, max_length=4)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'a%')
        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'ab%')
        setattr(o, 'attr', 'abcd')
        setattr(o, 'attr', 'abc%')
        self.assertRaises(ValueError, setattr, o, 'attr', 'a')
        self.assertRaises(ValueError, setattr, o, 'attr', '%')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcde')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd%')


class TestOrderedDict(TestCase):
    kvp = libyate.type.OrderedDict(
        (('job', 'cleanup'), ('job.done', '75%'), ('path', '/bin:/usr/bin:')))

    def test_from_tuple(self):
        self.assertEqual(self.kvp, libyate.type.OrderedDict(
            (('job', 'cleanup'), ('job.done', '75%'),
             ('path', '/bin:/usr/bin:'))))

    def test_from_list(self):
        self.assertEqual(self.kvp, libyate.type.OrderedDict(
            [['job', 'cleanup'], ['job.done', '75%'],
             ['path', '/bin:/usr/bin:']]))

    def test_from_ordered_dict(self):
        self.assertEqual(self.kvp, libyate.type.OrderedDict(self.kvp))

    def test_repr(self):
        self.assertEqual("libyate.type.OrderedDict((('job', 'cleanup'), "
                         "('job.done', '75%'), ('path', '/bin:/usr/bin:')))",
                         repr(self.kvp))

    def test_len(self):
        self.assertEqual(3, len(self.kvp))

    def test_access(self):
        self.assertEqual('cleanup', self.kvp['job'])
        self.assertEqual('75%', self.kvp['job.done'])
        self.assertEqual('/bin:/usr/bin:', self.kvp['path'])
        self.assertRaises(KeyError, self.kvp.__getitem__, 'a')

    def test_copy(self):
        new = self.kvp.copy()
        self.assertEqual(self.kvp, new)
        self.assertNotEqual(id(self.kvp), id(new))

    def test_reversed(self):
        self.assertEqual(list(reversed(self.kvp)),
                         list(reversed(list(self.kvp))))

    def test_delete(self):
        new = self.kvp.copy()
        del new['job']
        self.assertRaises(KeyError, new.__getitem__, 'job')


class TestYateStatus(TestCase):
    string = 'name=cdrbuild,type=cdr,format=Status|Caller|Called|BillId|' \
             'Duration;cdrs=5,hungup=0;sip/4=answered|test|99991007|' \
             '1403660477-4|12,sip/5=answered|test|99991007|1403660477-6|3,' \
             'sip/6=answered|test|99991007|1403660477-8|2,sip/7=answered|' \
             'test|99991007|1403660477-10|2,sip/8=answered|test|99991007|' \
             '1403660477-12|2'
    obj = libyate.type.YateStatus(string)

    def test_repr(self):
        self.assertEqual('<libyate.type.YateStatus "cdrbuild">',
                         repr(self.obj))

    def test_attrs(self):
        self.assertEqual('cdrbuild', self.obj.definition['name'])
        self.assertEqual('Status|Caller|Called|BillId|Duration',
                         self.obj.definition['format'])
        self.assertEqual('5', self.obj.status['cdrs'])
        self.assertEqual(5, len(self.obj.nodes))
        self.assertEqual('1403660477-4', self.obj.nodes['sip/4']['BillId'])
        self.assertEqual('99991007', self.obj.nodes['sip/4']['Called'])
        self.assertEqual('test', self.obj.nodes['sip/4']['Caller'])
        self.assertEqual('12', self.obj.nodes['sip/4']['Duration'])
        self.assertEqual('answered', self.obj.nodes['sip/4']['Status'])
