# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa


# x: Original input string.
# y: Processed string. For simplicity, y is only genreated by deleting some
#    characters from x
# return: marks of original x to indicate whether characters being removed or
# not.
def lcs_marks(x, y):
    # reverse inputs.
    x = tuple(reversed(x))
    y = tuple(reversed(y))

    nx = len(x)
    ny = len(y)

    # one-based.
    # nx * ny matrix.
    dp = [[None] * (ny + 1) for _ in range(nx + 1)]

    TO_TOP = 1
    TO_TOP_LEFT = 2

    for xi in range(nx + 1):
        for yi in range(min(xi + 1, ny + 1)):
            if xi == 0 or yi == 0:
                dp[xi][yi] = None
                continue
            if x[xi - 1] == y[yi - 1]:
                dp[xi][yi] = TO_TOP_LEFT
            else:
                dp[xi][yi] = TO_TOP

    marks = [False] * nx
    xi = nx
    yi = ny
    while yi > 0 and xi > 0:
        while dp[xi][yi] == TO_TOP:
            xi -= 1
        if dp[xi][yi] is None:
            raise RuntimeError
        # find TO_TOP_LEFT.
        marks[xi - 1] = True
        xi -= 1
        yi -= 1

    # reverse back.
    marks = tuple(reversed(marks))
    return marks
