# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from itertools import chain

from zh_doclint.lcs import lcs_marks
from zh_doclint.utils import text2lines, safelen


INT_MAX = 1 << 31 - 1


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

    def __init__(self, tag, row, col, val=None, parent=None):
        self.tag = tag
        self.row = row
        self.col = col
        self.val = val
        self.parent = parent

        self._attrs = (self.tag, self.row, self.col, self.val, self.parent)

    def __eq__(self, other):
        return self._attrs == other._attrs

    def __str__(self):
        return '<{0}>'.format(', '.join(map(str, self._attrs)))

    def __repr__(self):
        return str(self).encode('utf-8')


def add_diff_operations(attr, coordinates, diffs, val=None):
    func = getattr(DiffOperation, attr)
    ops = [func(x, y, val=val) for x, y in coordinates]
    diffs.extend(ops)


def delete_group(coordinates, diffs):
    add_diff_operations('delete', coordinates, diffs)


def insert_before(coordinate, diffs, val):
    add_diff_operations('insert', [coordinate], diffs, val=val)


def replace_with(coordinate, diffs, val):
    add_diff_operations('replace', [coordinate], diffs, val=val)


def correct_single_space_problem(element, match, handler):

    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
    )
    a, whitespaces, b = match.groups()

    if whitespaces:
        # delete all whitespaces.
        delete_group(coordinates[1], handler.diffs)

    # no whitespaces between a and b.
    # insert space between a and b.
    insert_before(coordinates[2][0], handler.diffs, val=' ')


def correct_e101(element, match, handler):
    correct_single_space_problem(element, match, handler)


def correct_e102(element, match, handler):
    correct_single_space_problem(element, match, handler)


def correct_e103(element, match, handler):
    correct_single_space_problem(element, match, handler)


def correct_e104(element, match, handler):
    match, tag = match
    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
    )
    whitespaces, lparenthesis, digits, rparenthesis = match.groups()

    # deal with spaces.
    if tag != 0:
        delete_group(coordinates[0], handler.diffs)
        if tag == 1:
            insert_before(coordinates[1][0], handler.diffs, val=' ')

    if lparenthesis != '(':
        replace_with(coordinates[1][0], handler.diffs, val='(')
    if rparenthesis != ')':
        replace_with(coordinates[3][0], handler.diffs, val=')')


class PunctuationConverter(object):

    EN2ZH = {
        # positive.
        '!': '！',
        '$': '＄',
        '(': '（',
        ')': '）',
        ',': '，',
        '.': '。',
        ':': '：',
        ';': '；',
        '<': '《',
        '>': '》',
        '?': '？',
        '\\': '、',
        '/': '、',
        '_': '＿',

        # best effort.
        '[': '「',
        ']': '」',
        '{': '『',
        '}': '』',

        # not sure.
        # https://en.wikipedia.org/wiki/Caret
        '^': '\u2038',
    }

    ZH2EN = {
        # positive.
        '！': '!',
        '＄': '$',
        '（': '(',
        '）': ')',
        '，': ',',
        '。': '.',
        '：': ':',
        '；': ';',
        '《': '<',
        '》': '>',
        '？': '?',
        '、': ',',
        '＿': '_',

        '‘': "'",
        '’': "'",
        '“': '"',
        '”': '"',

        # best effort.
        '「': '"',
        '」': '"',
        '『': '"',
        '』': '"',

        # not sure.
        # https://en.wikipedia.org/wiki/Caret
        '\u2038': '^',
    }


def correct_e201(element, match, handler):

    def guess_open_or_close(text, punctuation):
        return sum(map(lambda c: 1 if c == punctuation else 0, text)) % 2 == 0

    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
        offset=element.offset,
    )
    punctuation, whitespaces = match.groups()

    if punctuation in PunctuationConverter.EN2ZH:
        replace_with(
            coordinates[0][0], handler.diffs,
            val=PunctuationConverter.EN2ZH[punctuation],
        )
    else:
        # ' and "
        if guess_open_or_close(element.content[:match.start()], punctuation):
            val = '「'
        else:
            val = '」'
        replace_with(
            coordinates[0][0], handler.diffs, val=val,
        )

    if whitespaces:
        delete_group(coordinates[1], handler.diffs)


def correct_e202(element, match, handler):

    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
        offset=element.offset,
    )
    punctuation = match.group(1)

    if punctuation in PunctuationConverter.ZH2EN:
        replace_with(
            coordinates[0][0], handler.diffs,
            # because of E203, a space should be added to en punctuation.
            val=PunctuationConverter.ZH2EN[punctuation] + ' ',
        )


def correct_e203(element, match, handler):
    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
    )
    a, whitespaces, b = match.groups()

    if whitespaces:
        delete_group(coordinates[1], handler.diffs)


def correct_e204(element, match, handler):

    ZH_QUOTE_MAPPING = {
        '\u2018': '「',
        '\u201c': '「',
        '\u2019': '」',
        '\u201d': '」',
    }

    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
    )
    quote = match.group(1)
    replace_with(
        coordinates[0][0], handler.diffs,
        ZH_QUOTE_MAPPING[quote],
    )


def correct_e205(element, match, handler):

    coordinates = handler.coordinate_query.query_match(
        match, base_loc=element.loc_begin,
        add_right_boundary=True,
    )
    delete_group(coordinates[0], handler.diffs)
    insert_before(coordinates[1][0], handler.diffs, val='......')


def correct_e206(element, match, handler):
    pass


def correct_e207(element, match, handler):
    pass


def correct_e301(element, match, handler):
    pass


class CoordinateQuery(object):

    def __init__(self, index_matrix, lcs_matrix, parsed_lines):
        # line_size[i]: the number of characters in line i.
        line_size = [
            len(line)
            for line in chain('', map(lambda x: x or '', parsed_lines))
        ]

        # line_acc[i]: the number of characters from line 1 to line i.
        self.line_acc = [0] * len(line_size)
        for i in range(1, len(self.line_acc)):
            self.line_acc[i] = self.line_acc[i - 1] + line_size[i]

        self.parsed_lines = parsed_lines
        self.index_matrix = index_matrix
        self.lcs_matrix = lcs_matrix

    # mainly for testing.
    # return: text from line begin to line end, including end.
    def text(self, begin=1, end=None):
        end = end or len(self.parsed_lines) - 1
        end += 1
        return ''.join(map(lambda x: x or '', self.parsed_lines[begin:end]))

    # input:
    # offset: 0-based.
    # base_loc: 1-based.
    #
    # return: coordinate of original matrix.
    # row: 1-based.
    # col: 1-based.
    def query(self, parsed_offset, base_loc=1):
        base_acc = self.line_acc[base_loc - 1]
        lo = base_loc
        hi = len(self.line_acc) - 1
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if parsed_offset + 1 <= (self.line_acc[mid] - base_acc):
                hi = mid
            else:
                lo = mid + 1

        # 1-based row index.
        row = lo
        # 0-based.
        col = parsed_offset - self.line_acc[lo - 1] + base_acc
        # corner case: reach EOF.
        if (
            row == len(self.index_matrix) - 1 and
            col == len(self.index_matrix[row])
        ):
            return None, None

        # 1-based col index.
        col = self.index_matrix[row][col]
        return row, col

    # return:
    # [((x1, y1), (x2, y2), ...)...]
    def query_match(self, match, offset=0, base_loc=1,
                    add_right_boundary=False):
        match_offset = match.start()
        group_sizes = [len(g) for g in match.groups()]
        if add_right_boundary:
            group_sizes.append(1)

        coordinates = []
        acc = 0
        for size in group_sizes:
            if size == 0:
                coordinates.append([])
                continue

            start = self.query(match_offset + acc + offset, base_loc)
            end = self.query(match_offset + acc + offset + size - 1, base_loc)

            group_coordinates = []
            row, col = start
            # reach EOF.
            if row is None and col is None:
                coordinates.append(
                    [(INT_MAX, INT_MAX)]
                )
                break

            while (row, col) <= end:
                if self.lcs_matrix[row][col]:
                    group_coordinates.append(
                        (row, col),
                    )
                col += 1
                if col == len(self.lcs_matrix[row]):
                    row += 1
                    col = 0

            coordinates.append(group_coordinates)
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
        self.coordinate_query = CoordinateQuery(
            self.index_matrix, self.lcs_matrix, self.parsed_lines,
        )

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

        self.lcs_matrix = [[False] * (len(line) + 1) for line in lines]

        self.raw_lines = lines
        self.raw_lines[0] = None

        for element in elements:
            lbegin = element.loc_begin
            lend = element.loc_end

            x = ''.join(chain(*lines[lbegin:lend + 1]))
            y = element.content

            marks = lcs_marks(x, y)

            row = lbegin
            col = 1
            mi = 0
            while row <= lend:
                self.lcs_matrix[row][col] = marks[mi]
                mi += 1
                if col == len(self.lcs_matrix[row]) - 1:
                    row += 1
                    col = 1
                else:
                    col += 1

    def generate_parsed_lines(self, elements):
        self.parsed_lines = [None] * self.max_linenum
        for element in elements:
            lbegin = element.loc_begin
            for i, line in enumerate(text2lines(element.content)):
                self.parsed_lines[lbegin + i] = line

    def generate_index_matrix(self):
        self.index_matrix = [None] * self.max_linenum
        for row in range(1, self.max_linenum):
            parsed_line, ln = self.parsed_line(row)
            index_mapping = [None] * ln

            rawcol = 1
            for col in range(ln):
                while not self.lcs_matrix[row][rawcol]:
                    rawcol += 1
                index_mapping[col] = rawcol
                rawcol += 1

            self.index_matrix[row] = index_mapping

    def __call__(self, error_code, element, matches):
        corrector = globals()['correct_{0}'.format(error_code.lower())]
        for match in matches:
            corrector(element, match, self)
