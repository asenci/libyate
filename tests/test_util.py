"""
Test cases for libyate.util
"""

from libyate.util import yate_decode, yate_encode
from unittest import TestCase


class TestYateEncodeDecode(TestCase):
    strings = (
        ('75%%', '75%'),
        ('x%zz', 'x:z'),
        ('', ''),
    )

    for i in xrange(32):
        strings += (('%{0:c}'.format(i+64), chr(i)),)

    def test_decode_raise(self):
        self.assertRaises(Exception, yate_decode, '%%%')
        self.assertRaises(Exception, yate_decode, '%0')

    def test_encode_raise(self):
        self.assertRaises(Exception, yate_encode, None)
        self.assertRaises(Exception, yate_encode, 1)
        self.assertRaises(Exception, yate_encode, True)

for n, (e, d) in enumerate(TestYateEncodeDecode.strings):
    # noinspection PyDocstring
    def test_decode_ok(enc, dec):
        return lambda self: self.assertEqual(dec, yate_decode(enc))

    # noinspection PyDocstring
    def test_decode_nok(enc, dec):
        return lambda self: self.assertNotEqual(yate_decode(enc), dec + 'z')

    # noinspection PyDocstring
    def test_encode_ok(enc, dec):
        return lambda self: self.assertEqual(enc, yate_encode(dec))

    # noinspection PyDocstring
    def test_encode_nok(enc, dec):
        return lambda self: self.assertNotEqual(yate_encode(dec), enc + 'z')

    setattr(TestYateEncodeDecode, 'test_decode_ok_%s' % n,
            test_decode_ok(e, d))
    setattr(TestYateEncodeDecode, 'test_decode_nok_%s' % n,
            test_decode_nok(e, d))
    setattr(TestYateEncodeDecode, 'test_encode_ok_%s' % n,
            test_encode_ok(e, d))
    setattr(TestYateEncodeDecode, 'test_encode_nok_%s' % n,
            test_encode_nok(e, d))
