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
    nx = len(x)
    ny = len(y)

    # one-based.
    dp = [[None] * (ny + 1) for _ in range(nx + 1)]

    TO_LEFT = 1
    TO_TOP_LEFT = 2

    for i in range(nx + 1):
        for j in range(min(i + 1, ny + 1)):
            if i == 0 or j == 0:
                dp[i][j] = None
                continue
            if x[i - 1] == y[j - 1]:
                dp[i][j] = TO_TOP_LEFT
            else:
                dp[i][j] = TO_LEFT

    marks = [False] * nx
    i = nx
    j = ny
    while i > 0:
        while dp[i][j] == TO_LEFT:
            i -= 1
        if dp[i][j] is None:
            raise RuntimeError
        # find TO_TOP_LEFT.
        marks[i - 1] = True
        i -= 1
        j -= 1

    return marks
