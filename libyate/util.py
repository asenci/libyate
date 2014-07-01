"""
libyate - helper functions
"""

import re

from datetime import datetime

import libyate.cmd
import libyate.type


def cmd_from_string(string):
    """Parse the command string and return an Command object

    :param str string: Command string to parse
    :return: An Yate command object
    :rtype: Command
    :raise NotImplementedError: if the keyword in the command string is not
        supported
    """

    keyword, args = string.split(':', 1)

    cmd_cls = libyate.cmd.KW_CLS_MAP.get(keyword)

    if cmd_cls is None:
        raise NotImplementedError('Keyword "{0}" not implemented'
                                  .format(keyword))

    cmd_obj = cmd_cls.__new__(cmd_cls)
    args = args.split(':', len(cmd_cls.__descriptors__) - 1)

    # Map arguments to descriptors
    for desc, value in zip(cmd_cls.__descriptors__,
                           args):

        # Decode upcoded strings
        if isinstance(desc, libyate.type.String) and desc.encoded:
            value = yate_decode(value)

        desc.__set__(cmd_obj, value)

    return cmd_obj


def timestamp_as_str(dt):
    """Return a timestamp string from the datetime object

    :param datetime.datetime dt: A datetime object
    :return: A timestamp string
    :rtype: str
    """

    return str(int((dt - datetime(1970, 1, 1)).total_seconds()))


def yate_decode(string):
    """Decode Yate up-coded strings

    :param str string: An encoded (Yate up-coded) string
    :return: A decoded (Yate down-coded) string
    :rtype: str
    """

    # noinspection PyDocstring
    def replace(m):
        if m.group(1) == '%':
            return '%'
        else:
            return chr(ord(m.group(1)) - 64)

    return re.sub(r'%(.?)', replace, string)


def yate_encode(string):
    """Encode string using Yate up-coded representation

    :param str string: A string
    :return: A encoded (Yate up-coded) string
    :rtype: str
    """

    special_chars = ''.join([chr(i) for i in xrange(32)] + ['%', ':', '='])

    # noinspection PyDocstring
    def replace(m):
        if m.group() == '%':
            return '%%'
        else:
            return '%{0:c}'.format(ord(m.group()) + 64)

    return re.sub(r'[{0}]'.format(special_chars), replace, string)


def yate_str(obj):
    """Return the Yate string representation for the object

    :param object obj: An object
    :return: A string representing the object
    :rtype: str
    """

    if obj is None:
        return ''

    elif isinstance(obj, (str, unicode)):
        return obj

    elif isinstance(obj, bool):
        return 'true' if obj else 'false'

    elif isinstance(obj, libyate.type.OrderedDict):
        return ':'.join(('='.join((
            yate_encode(yate_str(k)),
            yate_encode(yate_str(v)),
        )).rstrip('=') for k, v in obj.items()))

    else:
        if isinstance(obj, datetime):
            return timestamp_as_str(obj)

        return str(obj)
