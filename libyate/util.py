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
