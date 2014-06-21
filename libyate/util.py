"""
libyate - helper functions
"""


def yate_decode(string):
    """Decode Yate upcoded strings"""
    import re

    def replace(m):
        if m.group(1) == '%':
            return '%'
        else:
            return chr(ord(m.group(1)) - 64)

    return re.sub(r'%(.?)', replace, string)


def yate_encode(string):
    """Encode string into Yate upcoded representation"""
    import re

    special_chars = ''.join([chr(i) for i in range(32)] + ['%', ':', '='])

    def replace(m):
        if m.group() == '%':
            return '%%'
        else:
            return '%{0:c}'.format(ord(m.group()) + 64)

    return re.sub(r'[{0}]'.format(special_chars), replace, string)


def yate_str(obj):
    from libyate.type import OrderedDict

    if obj is None:
        return ''

    elif isinstance(obj, (str, unicode)):
        return obj

    elif isinstance(obj, bool):
        return 'true' if obj else 'false'

    elif isinstance(obj, OrderedDict):
        return ':'.join(('='.join((
            yate_encode(yate_str(k)),
            yate_encode(yate_str(v)),
        )).rstrip('=') for (k, v) in obj.items()))

    else:
        from datetime import datetime
        if isinstance(obj, datetime):
            return str(int((obj - datetime(1970, 1, 1)).total_seconds()))

        return str(obj)
