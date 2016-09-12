# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from zhlint.lcs import lcs_marks


def test_simple():
    x = 'abbc'
    y = 'abc'

    assert [True, False, True, True] == lcs_marks(x, y)


def test_header():
    x = '### abcd'
    y = 'abc'

    expected = [False] * len(x)
    expected[4:7] = [True] * 3
    assert expected == lcs_marks(x, y)
