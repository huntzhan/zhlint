# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import collections as abc
from io import StringIO
from os.path import expanduser


def load_file(fpath):
    fpath = expanduser(fpath)
    with open(fpath, encoding='utf-8') as fin:
        return fin.read()


def write_file(fpath, content):
    fpath = expanduser(fpath)
    with open(fpath, encoding='utf-8', mode='w') as fout:
        fout.write(content)


def try_invoke(inst, method_name):
    method = getattr(inst, method_name, None)
    if callable(method):
        method()


def text2lines(text):
    with StringIO(text) as sin:
        return sin.readlines()


def safelen(line):
    return 0 if not isinstance(line, abc.Sized) else len(line)


def count_newlines(e):
    if isinstance(e, str):
        return count_newlines_in_str(e)
    else:
        return count_newlines_in_match(e)


def count_newlines_in_str(text):
    count = 0
    for c in text:
        if c == '\n':
            count += 1
    return count


def count_newlines_in_match(m):
    return count_newlines_in_str(m.group(0))


def count_offset(prefix):
    offset = 0
    for c in reversed(prefix):
        if c == '\n':
            break
        else:
            offset += 1
    return offset


class TextElement(object):

    def __init__(self, block_type, loc_begin, loc_end, content, offset=0):
        self.block_type = block_type
        self.loc_begin = int(loc_begin)
        self.loc_end = int(loc_end)
        self.content = content
        self.offset = offset
