"""
libyate - custom types and descriptors
"""

from libyate.util import yate_decode, yate_encode


#
# Meta classes
#

class TypeMeta(type):
    """Metaclass for classes with descriptor declarations"""

    def __new__(mcs, name, bases, attrs):
        # Define attribute name for BaseType instances
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, BaseType):
                attr_value.__name__ = attr_name

        return super(TypeMeta, mcs).__new__(mcs, name, bases, attrs)


#
# Custom types
#

class kv_tuple(tuple):
    """Tuple of key-value pairs"""

    def __init__(self, seq=()):
        super(kv_tuple, self).__init__(seq)
        self.__keys__, self.__values__ = zip(*self)

    def __getitem__(self, item):
        if isinstance(item, int):
            return super(kv_tuple, self).__getitem__(item)

        try:
            idx = self.__keys__.index(item)
        except ValueError:
            raise KeyError(item)

        return self.__values__[idx]

    def __repr__(self):
        return '{0}.{1}({2})'.format(
            self.__class__.__module__, self.__class__.__name__,
            super(kv_tuple, self).__repr__())


#
# Descriptors
#

class BaseType(object):

    __count__ = 0
    blank = None

    def __init__(self, blank=False):
        if blank is not None:
            self.blank = blank

        self.__instance_number__ = BaseType.__count__
        BaseType.__count__ += 1

    def __repr__(self):
        return '<{0}.{1} "{2}">'.format(
            self.__class__.__module__, self.__class__.__name__, self.__name__)

    # noinspection PyUnusedLocal
    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = self.format_for_get(instance.__dict__.get(self.__name__))

        if value is None and not self.blank:
            raise ValueError('{0!r} can not be blank'.format(self))

        return value

    def __set__(self, instance, value):
        try:
            value = self.format_for_set(value)

            if value is None and self.blank is False:
                raise ValueError('{0!r} can not be blank'.format(self))

            instance.__dict__[self.__name__] = value

        except TypeError as e:
            if str(e):
                raise
            else:
                raise TypeError('Invalid type "{0}" for descriptor {1!r}'
                                .format(type(value).__name__, self))

    def __delete__(self, instance):
        if self.__name__ in instance.__dict__:
            del instance.__dict__[self.__name__]

    def format_for_get(self, value):
        return value

    def format_for_set(self, value):
        if value is not None:
            self.format_for_get(value)

        return value


class String(BaseType):

    length = None
    min_length = None
    max_length = None

    def __init__(self, blank=False, length=None, min_length=None,
                 max_length=None):
        super(String, self).__init__(blank=blank)

        if length is not None:
            self.length = length

        if self.length is not None:
            self.min_length = self.max_length = self.length

        else:
            if min_length is not None:
                self.min_length = min_length
            if max_length is not None:
                self.max_length = max_length

    def format_for_get(self, value):
        if value is None:
            return

        elif isinstance(value, (str, unicode)):
            if self.min_length and len(value) < self.min_length:
                raise ValueError('String is too short: "{0}"'.format(value))
            if self.max_length and len(value) > self.max_length:
                raise ValueError('String is too long: "{0}"'.format(value))

            return super(String, self).format_for_get(value)

        raise TypeError

    def format_for_set(self, value):
        if value is None:
            return

        elif isinstance(value, bool):
            value = 'true' if value else 'false'

        elif isinstance(value, int):
            value = str(value)

        if isinstance(value, (str, unicode)):
            if value or self.blank:
                return super(String, self).format_for_set(value or None)

            raise ValueError('{0!r} can not be blank'.format(self))

        raise TypeError


class Boolean(String):

    def __init__(self, blank=False):
        super(Boolean, self).__init__(blank=blank)

    def format_for_get(self, value):
        if value is None:
            return

        elif value in ['true', 'false']:
            return super(Boolean, self).format_for_get(value) == 'true'

        raise ValueError('{0} is neither "true" or "false"')

    def format_for_set(self, value):
        if value is None or isinstance(value, (str, unicode, bool)):
            return super(Boolean, self).format_for_set(value)

        raise TypeError


class EncodedString(String):
    def format_for_get(self, value):
        if value is not None:
            return super(EncodedString, self).format_for_get(
                yate_decode(value))

    def format_for_set(self, value):
        if value is None:
            return

        elif isinstance(value, (str, unicode)):
            return super(EncodedString, self).format_for_set(
                yate_encode(value))

        elif isinstance(value, (int, bool)):
            return yate_encode(super(EncodedString, self).format_for_set(
                value))

        raise TypeError


class Integer(String):

    def __init__(self, blank=False):
        super(Integer, self).__init__(blank=blank)

    def format_for_get(self, value):
        if value is not None:
            return int(super(Integer, self).format_for_get(value))

    def format_for_set(self, value):
        if value is None or isinstance(value, (str, unicode, int)):
            return super(Integer, self).format_for_set(value)

        raise TypeError


class KeyValueTuple(String):

    def __init__(self, blank=False):
        super(KeyValueTuple, self).__init__(blank=blank)

    def format_for_get(self, value):
        if value is not None:
            return kv_tuple(
                tuple(yate_decode(s) for s in x.partition('=')[::2]) for x in
                super(KeyValueTuple, self).format_for_get(value).split(':')
            )

    def format_for_set(self, value):
        if isinstance(value, (dict, list, set, tuple)):
            if isinstance(value, dict):
                value = value.items()

            value = ':'.join(
                '='.join([
                    EncodedString().format_for_set(k),
                    EncodedString().format_for_set(v)
                ]).rstrip('=') for k, v in value
            )

        if value is not None:
            return super(KeyValueTuple, self).format_for_set(value)


class DateTime(Integer):

    def format_for_get(self, value):
        if value is not None:
            from datetime import datetime

            return datetime.utcfromtimestamp(
                super(DateTime, self).format_for_get(value))

    def format_for_set(self, value):
        from datetime import datetime

        if isinstance(value, datetime):
            value = str(int((value - datetime(1970, 1, 1)).total_seconds()))

        if value is not None:
            return super(DateTime, self).format_for_set(value)
