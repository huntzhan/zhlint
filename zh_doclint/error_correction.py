# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from io import StringIO
from itertools import chain

from zh_doclint.lcs import lcs_marks


class ErrorCorrectionHandler(object):

    # build block-level LCS.
    def __init__(self, file_content, elements):
        elements = elements[:-1]
        # init self.lcs_matrix and self.lines
        self.generate_lcs_matrix(file_content, elements)

    def generate_lcs_matrix(self, file_content, elements):
        with StringIO(file_content) as sin:
            lines = sin.readlines()
        # one-based.
        lines.insert(0, [])

        self.lcs_matrix = [[False] * len(line) for line in lines]
        self.lines = lines

        for element in elements:
            lbegin = int(element.loc_begin)
            lend = int(element.loc_end)

            x = ''.join(chain(*lines[lbegin:lend + 1]))
            y = element.content

            marks = lcs_marks(x, y)
            row = lbegin
            col = 0
            mi = 0
            while row <= lend:
                self.lcs_matrix[row][col] = marks[mi]
                mi += 1
                if col == len(self.lcs_matrix[row]) - 1:
                    row += 1
                    col = 0
                else:
                    col += 1

    def __call__(self, error_code, element, matches):
        pass
