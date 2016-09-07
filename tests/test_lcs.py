# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from zh_doclint.lcs import lcs_marks


def test_simple():
    x = 'abbc'
    y = 'abc'

    assert [True, False, True, True] == lcs_marks(x, y)
