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

    assert [True, True, False, True] == lcs_marks(x, y)


def test_header():
    x = '### abcd'
    y = 'abc'

    expected = [False] * len(x)
    expected[4:7] = [True] * 3
    assert expected == lcs_marks(x, y)


def test_newline():
    x = 'a\n\nb'
    y = 'a\nb'

    expected = [True, True, False, True]
    assert expected == lcs_marks(x, y)


def test_latex():
    x = '3. 第 (5) 步的重定向 transitions $ChildrenTrans$.\n'
    y = '第 (5) 步的重定向 transitions $$.\n'
    expected = [True] * len(x)
    expected[0:3] = [False] * 3
    expected[28:41] = [False] * (41 - 28)
    assert expected == lcs_marks(x, y)
