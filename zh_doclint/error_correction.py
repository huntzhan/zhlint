# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from itertools import chain

from zh_doclint.lcs import lcs_marks
from zh_doclint.utils import text2lines, safelen


class Diff(object):
    INSERT = 0
    DELETE = 1
    REPLACE = 2


def correct_e101(error_code, element, matches, diffs):
    pass


def correct_e102(error_code, element, matches, diffs):
    pass


def correct_e103(error_code, element, matches, diffs):
    pass


def correct_e104(error_code, element, matches, diffs):
    pass


def correct_e201(error_code, element, matches, diffs):
    pass


def correct_e202(error_code, element, matches, diffs):
    pass


def correct_e203(error_code, element, matches, diffs):
    pass


def correct_e204(error_code, element, matches, diffs):
    pass


def correct_e205(error_code, element, matches, diffs):
    pass


def correct_e206(error_code, element, matches, diffs):
    pass


def correct_e207(error_code, element, matches, diffs):
    pass


def correct_e301(error_code, element, matches, diffs):
    pass


class ErrorCorrectionHandler(object):

    # build block-level LCS.
    def __init__(self, file_content, elements):
        elements = elements[:-1]
        # init self.lcs_matrix and self.raw_lines
        self.generate_lcs_matrix(file_content, elements)
        # init self.parsed_lines
        self.generate_parsed_lines(elements)
        # init self.index_matrix
        self.generate_index_matrix()

        # store diff operations.
        # [(row, col, mark)...].
        # mark: one of INSERT, DELETE, REPLACE.
        # row, col: position of parsed content.
        self.diffs = []

    @property
    def max_linenum(self):
        return len(self.raw_lines)

    def raw_line(self, i):
        return self.raw_lines[i], safelen(self.raw_lines[i])

    def parsed_line(self, i):
        return self.parsed_lines[i], safelen(self.parsed_lines[i])

    def generate_lcs_matrix(self, file_content, elements):
        # one-based.
        lines = text2lines(file_content)
        lines.insert(0, [])

        self.lcs_matrix = [[False] * len(line) for line in lines]

        self.raw_lines = lines
        self.raw_lines[0] = None

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

    def generate_parsed_lines(self, elements):
        self.parsed_lines = [None] * self.max_linenum
        for element in elements:
            lbegin = int(element.loc_begin)
            for i, line in enumerate(text2lines(element.content)):
                self.parsed_lines[lbegin + i] = line

    def generate_index_matrix(self):
        self.index_matrix = [None] * self.max_linenum
        for row in range(1, self.max_linenum):
            parsed_line, ln = self.parsed_line(row)
            index_mapping = [None] * ln

            rawcol = 0
            for col in range(ln):
                while not self.lcs_matrix[row][rawcol]:
                    rawcol += 1
                index_mapping[col] = rawcol
                rawcol += 1

            self.index_matrix[row] = index_mapping

    def __call__(self, error_code, element, matches):
        corrector = globals()['correct_{0}'.format(error_code.lower())]
        corrector(error_code, element, matches, self.diffs)
