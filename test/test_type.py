"""
Test cases for libyate.type
"""

import libyate.type
from unittest import TestCase


#
# Meta classes
#

class TypeCaseMeta(type):
    """Meta class for YateCmd test cases"""

    def __new__(mcs, name, bases, attrs):
        # Get command class
        type_class = attrs.get('type_class')

        # Get strings
        values = attrs.get('values', ())

        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = type_class(blank=True)
            not_blank = type_class()

        o = C()

        for n, (v, r) in enumerate(values):
            def test_value_repr(obj, val, rep):
                def test(self):
                    setattr(obj, 'attr', val)
                    self.assertEqual(rep, obj.__dict__['attr'])

                return test

            def test_blank(obj):
                def test(self):
                    self.assertRaises(
                        ValueError, setattr, obj, 'not_blank', None)

                return test

            attrs['test_value_repr_%s' % n] = test_value_repr(o, v, r)
            attrs['test_blank'] = test_blank(o)

        return super(TypeCaseMeta, mcs).__new__(mcs, name, bases, attrs)


#
# Test cases
#

class TestBaseType(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.BaseType
    values = (
        ('', ''),
        ('a', 'a'),
        (('a',), ('a',)),
        (0, 0),
        (None, None),
        (True, True),
        (u'a', u'a'),
    )

    def test_repr(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = self.type_class()

        self.assertEqual('<libyate.type.BaseType "attr">', repr(C.attr))

    def test_delete(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.BaseType()

        o = C()
        self.assertTrue('attr' not in o.__dict__)

        o.attr = 'a'
        self.assertTrue('attr' in o.__dict__)

        del o.attr
        self.assertTrue('attr' not in o.__dict__)


class TestString(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.String
    values = (
        ('', None),
        ('a', 'a'),
        (0, '0'),
        (None, None),
        (True, 'true'),
        (u'a', u'a'),
    )

    def test_raises(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', '')
        self.assertRaises(TypeError, setattr, o, 'attr', ('a',))

    def test_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')

    def test_max_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(max_length=3)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'abc')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')

    def test_min_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(min_length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')

    def test_max_min_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(min_length=2, max_length=4)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'a')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcde')


class TestBoolean(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.Boolean
    values = (
        ('false', 'false'),
        ('true', 'true'),
        (False, 'false'),
        (None, None),
        (True, 'true'),
    )

    def test_raises(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', 'tru')
        self.assertRaises(TypeError, setattr, o, 'attr', 0)


class TestEncodedString(TestCase):

    __metaclass__ = TypeCaseMeta

    type_class = libyate.type.EncodedString
    values = (
        ('', None),
        ('a', 'a'),
        (u'a', u'a'),
        ('%', '%%'),
        (0, '0'),
        (None, None),
        (True, 'true'),
    )

    def test_raises(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = self.type_class()

        o = C()

        self.assertRaises(ValueError, setattr, o, 'attr', '')
        self.assertRaises(TypeError, setattr, o, 'attr', ('a',))

    def test_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')

    def test_max_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(max_length=3)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'abc')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcd')

    def test_min_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(min_length=3)

        o = C()

        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'ab')

    def test_max_min_length(self):
        class C(object):
            __metaclass__ = libyate.type.TypeMeta

            attr = libyate.type.String(min_length=2, max_length=4)

        o = C()

        setattr(o, 'attr', 'ab')
        setattr(o, 'attr', 'abc')
        setattr(o, 'attr', 'abcd')
        self.assertRaises(ValueError, setattr, o, 'attr', 'a')
        self.assertRaises(ValueError, setattr, o, 'attr', 'abcde')


