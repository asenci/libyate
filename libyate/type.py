"""
libyate - custom types and descriptors
"""

from abc import ABCMeta, abstractmethod
from collections import MutableMapping
from datetime import datetime

import libyate.util


#
# Custom types
#

class OrderedDict(MutableMapping, dict):
    """Dictionary that remembers insertion order. Useful for editing XML files
    and config files where there are (key, value) pairs but the original order
    should be preserved.
    http://code.activestate.com/recipes/576669/"""

    # noinspection PyMissingConstructor
    def __init__(self, seq=(), **kwargs):
        if not hasattr(self, '_keys'):
            self._keys = []

        self.update(seq, **kwargs)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if key not in self:
            self._keys.append(key)

        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        self._keys.remove(key)

        dict.__delitem__(self, key)

    def __iter__(self):
        return iter(self._keys)

    def __reversed__(self):
        return reversed(self._keys)

    def __len__(self):
        return len(self._keys)

    def __repr__(self):
        return '{0}.{1}({2})'.format(
            self.__class__.__module__, self.__class__.__name__,
            tuple(tuple((k, v)) for k, v in self.items()))

    def copy(self):
        """D.copy() -> a shallow copy of D"""

        return self.__class__(self)


class YateStatus(object):
    """Object representing an Yate status message"""

    def __init__(self, string):
        """:param str string: string to decode"""

        # Definition, status and nodes groups are separated by ';'
        definition, status = string.partition(';')[::2]
        status, nodes = status.partition(';')[::2]

        # Attributes are represented by key=value pairs separated by ','
        self.definition = dict((x.partition('=')[::2])
                               for x in definition.split(','))
        self.status = dict((x.partition('=')[::2])
                           for x in status.split(','))
        self.nodes = dict((x.partition('=')[::2])
                          for x in nodes.split(','))

        # Nodes attributes are separated by '|'
        # Attributes names are optionally defined on the 'format' attribute
        if self.definition.get('format') is not None:
            fmt = self.definition.get('format').split('|')
            for k, v in self.nodes.items():
                self.nodes[k] = dict(zip(fmt, v.split('|')))

    def __repr__(self):
        return '<{0}.{1} "{2}">'.format(
            self.__class__.__module__, self.__class__.__name__,
            self.definition.get('name', 'undefined'))


#
# Meta classes
#

class DescriptorMeta(ABCMeta):
    """Metaclass for classes with descriptor declarations"""

    def __new__(mcs, name, bases, attrs):
        # Define attribute name for Descriptor instances
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Descriptor):
                attr_value.__name__ = attr_name

        # Get all attributes from class and its base classes
        all_attrs = {}

        for cls in reversed(bases):
            all_attrs.update(cls.__dict__)

        all_attrs.update(attrs)

        # Build a sorted list of all descriptors
        attrs['__descriptors__'] = sorted(
            [v for k, v in all_attrs.items() if isinstance(v, Descriptor)],
            key=lambda x: x.__instance_number__)

        return super(DescriptorMeta, mcs).__new__(mcs, name, bases, attrs)


#
# Descriptors
#

class Descriptor(object):
    """Base descriptor

    :param bool blank: Allow value to be None
    """
    __count__ = 0

    blank = False

    def __init__(self, blank=None):
        if blank is not None:
            self.blank = blank

        self.__instance_number__ = Descriptor.__count__
        Descriptor.__count__ += 1

    def __repr__(self):
        return '<{0}.{1} "{2}">'.format(
            self.__class__.__module__, self.__class__.__name__, self.__name__)

    # noinspection PyUnusedLocal
    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(self.__name__)

    def __set__(self, instance, value):
        try:
            value = self.format(value)

            if value is not None or self.blank:
                instance.__dict__[self.__name__] = value

            else:
                raise ValueError

        except (TypeError, ValueError) as e:
            if str(e):
                raise

            elif isinstance(e, ValueError):
                raise ValueError('{0!r} can not be blank'.format(self))

            else:
                raise TypeError('Invalid type "{0}" for descriptor {1!r}'
                                .format(type(value).__name__, self))

    def __delete__(self, instance):
        if self.__name__ in instance.__dict__:
            del instance.__dict__[self.__name__]

    @abstractmethod
    def format(self, value):
        """Format value before assignment

        :param object value: value to be formatted
        :return: formatted value
        :rtype: object

        :raise: ValueError: if value is not acceptable
        :raise: TypeError: if value type is not acceptable
        """

        return value

    def to_string(self, instance):
        """Convert value into string

        :param object instance: object instance where the value is stored
        :return: string representing the object
        :rtype: str
        """

        if instance:
            return libyate.util.yate_str(
                self.__get__(instance, instance.__class__))


class Boolean(Descriptor):
    """Descriptor representing a boolean value"""

    def format(self, value):
        """Format value before assignment

        :param value: value to be formatted
        :type value: str or bool
        :return: boolean
        :rtype: bool
        :raise ValueError: if string is not "true" or "false"
        :raise TypeError: if value type is not acceptable
        """

        if value in [None, '']:
            return

        elif isinstance(value, bool):
            return value

        elif isinstance(value, (str, unicode)):
            if value in ['true', 'false']:
                return value == 'true'

            raise ValueError('Value must be "true" or "false" for {0!r}'
                             .format(self))

        raise TypeError


class DateTime(Descriptor):
    """Descriptor representing a datetime object"""

    def format(self, value):
        """Format value before assignment

        :param value: value to be formatted
        :type value: str or int or datetime.datetime
        :return: a datetime object
        :rtype: datetime.datetime
        :raise ValueError: if the string or integer are not a valid timestamp
        :raise TypeError: if value type is not acceptable
        """
        if value in [None, '']:
            return

        if isinstance(value, datetime):
            return value

        elif isinstance(value, bool):
            raise TypeError

        elif isinstance(value, (int, str, unicode)):
            if isinstance(value, (str, unicode)):
                value = int(value)

            return datetime.utcfromtimestamp(value)

        raise TypeError


class Integer(Descriptor):
    """Descriptor representing an integer"""

    def format(self, value):
        """Format value before assignment

        :param value: value to be formatted
        :type value: str or int
        :return: an integer
        :rtype: int
        :raise ValueError: if the string is not a valid integer
        :raise TypeError: if value type is not acceptable
        """
        if value in [None, '']:
            return

        elif isinstance(value, bool):
            raise TypeError

        if isinstance(value, int):

            return value

        elif isinstance(value, (str, unicode)):
            return int(value)

        raise TypeError


class KeyValueList(Descriptor):
    """Descriptor representing an ordered dictionary"""

    def format(self, value):
        """Format value before assignment

        :param value: value to be formatted
        :type value: dict or list or set or tuple or OrderedDict
        :return: an OrderedDict object
        :rtype: OrderedDict
        :raise ValueError: if the string is not a valid key-value enumeration
        :raise ValueError: if any key in the key-value pair are empty
        :raise TypeError: if value type is not acceptable
        """

        if value in [None, '']:
            return

        elif isinstance(value, OrderedDict):
            return value

        elif isinstance(value, (dict, list, set, tuple)):
            return OrderedDict(value)

        elif isinstance(value, (str, unicode)):
            result = []

            for k, v in (x.partition('=')[::2] for x in value.split(':')):
                if k == '':
                    raise ValueError('Key on key-value pair cannot be empty')

                result.append((libyate.util.yate_decode(k),
                               libyate.util.yate_decode(v)))

            return OrderedDict(result)

        raise TypeError


class String(Descriptor):
    """Descriptor representing a string

    :param bool blank: Allow value to be None or ''
    :param bool encoded: Format string as a Yate encoded (up-coded) string
    :param int length: String length
    :param int min_length: String minimal length
    :param int max_length: String maximal length
    """

    encoded = False
    length = None
    min_length = None
    max_length = None

    def __init__(self, blank=None, encoded=None, length=None,
                 min_length=None, max_length=None):
        super(String, self).__init__(blank=blank)

        if encoded is not None:
            self.encoded = encoded

        if length is not None:
            self.length = length

        if self.length is not None:
            self.min_length = self.max_length = self.length

        else:
            if min_length is not None:
                self.min_length = min_length
            if max_length is not None:
                self.max_length = max_length

    def format(self, value):
        """Format value before assignment

        :param value: value to be formatted
        :type value: bool or int or datetime.datetime or str
        :return: a string
        :rtype: str
        :raise ValueError: if the string length is not acceptable
        :raise TypeError: if value type is not acceptable
        """

        if value in [None, '']:
            return

        elif isinstance(value, bool):
            value = 'true' if value else 'false'

        elif isinstance(value, int):
            value = str(value)

        elif isinstance(value, datetime):
            value = libyate.util.timestamp_as_str(value)

        if isinstance(value, (str, unicode)):
            if value or self.blank:
                if self.min_length and len(value) < self.min_length:
                    raise ValueError('String too short for {0!r}'.format(self))
                if self.max_length and len(value) > self.max_length:
                    raise ValueError('String too long for {0!r}'.format(self))

                return value or None

            raise ValueError

        raise TypeError

    def to_string(self, instance):
        """Encode string

        :param object instance: object instance where the value is stored
        :return: encoded (Yate up-coded) string
        :rtype: str
        """

        result = super(String, self).to_string(instance)

        if self.encoded:
            return libyate.util.yate_encode(result)
        else:
            return result
