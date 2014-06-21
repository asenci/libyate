"""
libyate - Python library for developing Yate external modules


Copyright (c) 2013 Andre Sencioles Vitorio Oliveira <andre@bcp.net.br>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""


def cmd_from_string(string):
    from libyate.cmd import KW_MAP
    from libyate.type import EncodedString
    from libyate.util import yate_decode

    # Get keyword from the command string
    keyword, args = string.split(':', 1)

    # Find the command class
    cmd_cls = KW_MAP.get(keyword)

    if cmd_cls is None:
        raise NotImplementedError(
            'Keyword "{0}" not implemented'.format(keyword))

    # Descriptors list
    desc_list = cmd_cls.__descriptors__

    # Number of attributes to extract from the command string
    num_attrs = len(desc_list) - 1

    # New command object
    cmd_obj = cmd_cls.__new__(cmd_cls)

    # Map arguments to descriptors
    map(lambda d, v: d.__set__(
        cmd_obj, d.format_for_get(v or None)),
        desc_list, args.split(':', num_attrs))

    return cmd_obj