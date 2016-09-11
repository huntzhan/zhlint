# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re

from zh_doclint.error_correction import ErrorCorrectionHandler
from zh_doclint.utils import TextElement


SIMPLE_CONTENT = (
    'abc\n'
    '\n'
    'abc'
)
SIMPLE_ELEMENTS = (
    TextElement('paragraph', '1', '1', 'ac\n'),
    TextElement('paragraph', '3', '3', 'ac'),
    'EOF',
)


def test_generate_lcs_matrix():

    h = ErrorCorrectionHandler(SIMPLE_CONTENT, SIMPLE_ELEMENTS)

    l1 = [True] * len(h.raw_lines[1])
    l1[1] = False
    assert l1 == h.lcs_matrix[1]

    l3 = [True] * len(h.raw_lines[3])
    l3[1] = False
    assert l3 == h.lcs_matrix[3]

    l1 = [0, 2, 3]
    assert l1 == h.index_matrix[1]

    l3 = [0, 2]
    assert l3 == h.index_matrix[3]


def test_coordinate_query():

    h = ErrorCorrectionHandler(SIMPLE_CONTENT, SIMPLE_ELEMENTS)
    q = h.coordinate_query

    assert (1, 0) == q.query(0)
    assert (1, 2) == q.query(2)
    assert (3, 0) == q.query(3)
    assert (3, 1) == q.query(4)

    assert (3, 0) == q.query(0, base_loc=3)
    assert (3, 1) == q.query(1, base_loc=3)

    text = q.text()
    m = re.search(r'(ac)(\s+)(ac)', text)
    assert [
        ((1, 0), (1, 1)),
        ((1, 2), (1, 2)),
        ((3, 0), (3, 1)),
    ] == q.query_match(m)

    text = q.text(2, 3)
    print(text)
    m = re.search(r'(ac)', text)
    assert [
        ((3, 0), (3, 1)),
    ] == q.query_match(m, base_loc=2)
