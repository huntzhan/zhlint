# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from itertools import chain

from zh_doclint.lcs import lcs_marks
from zh_doclint.utils import text2lines, safelen


class DiffOperation(object):

    INSERT = 0
    DELETE = 1
    REPLACE = 2

    @staticmethod
    def insert(*args, **kwargs):
        return DiffOperation(DiffOperation.INSERT, *args, **kwargs)

    @staticmethod
    def delete(*args, **kwargs):
        return DiffOperation(DiffOperation.DELETE, *args, **kwargs)

    @staticmethod
    def replace(*args, **kwargs):
        return DiffOperation(DiffOperation.REPLACE, *args, **kwargs)

    def __init__(self, tag, row, col, parent=None):
        self.tag = tag
        self.row = row
        self.col = col
        self.parent = parent


def correct_e101(error_code, element, matches, handler):
    pass


def correct_e102(error_code, element, matches, handler):
    pass


def correct_e103(error_code, element, matches, handler):
    pass


def correct_e104(error_code, element, matches, handler):
    pass


def correct_e201(error_code, element, matches, handler):
    pass


def correct_e202(error_code, element, matches, handler):
    pass


def correct_e203(error_code, element, matches, handler):
    pass


def correct_e204(error_code, element, matches, handler):
    pass


def correct_e205(error_code, element, matches, handler):
    pass


def correct_e206(error_code, element, matches, handler):
    pass


def correct_e207(error_code, element, matches, handler):
    pass


def correct_e301(error_code, element, matches, handler):
    pass


class CoordinateQuery(object):

    def __init__(self, parsed_lines):
        # line_acc[i]: the number of characters from line 1 to line i.
        self.line_acc = [
            len(line)
            for line in chain('', map(lambda x: x or '', parsed_lines))
        ]
        for i in range(2, len(self.line_acc)):
            self.line_acc[i] += self.line_acc[i - 1]

        self.parsed_lines = parsed_lines

    # mainly for testing.
    # return: text from line begin to line end, including end.
    def text(self, begin=1, end=None):
        end = end or len(self.parsed_lines) - 1
        end += 1
        return ''.join(map(lambda x: x or '', self.parsed_lines[begin:end]))

    # input:
    # offset: 0-based.
    # base_loc: 1-based.
    # return:
    # row: 1-based.
    # col: 0-based.
    def query(self, offset, base_loc=1):
        base_acc = self.line_acc[base_loc - 1]
        lo = base_loc
        hi = len(self.line_acc) - 1
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if offset + 1 <= (self.line_acc[mid] - base_acc):
                hi = mid
            else:
                lo = mid + 1

        row = lo
        col = 0
        offset -= (self.line_acc[row - 1] - base_acc)

        while offset > 0:
            offset -= 1
            col += 1

        return row, col

    # return:
    # [((x1, y1), (x2, y2))...]
    def query_match(self, match, offset=0, base_loc=1):
        match_offset = match.start()
        group_sizes = [len(g) for g in match.groups()]

        coordinates = []
        acc = 0
        for size in group_sizes:
            start = self.query(match_offset + acc + offset, base_loc)
            end = self.query(match_offset + acc + offset + size - 1, base_loc)
            coordinates.append(
                (start, end),
            )
            acc += size

        return coordinates


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
        self.diffs = []

        # init CoordinateQuery.
        self.coordinate_query = CoordinateQuery(self.parsed_lines)

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
