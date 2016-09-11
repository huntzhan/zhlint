# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re

from zh_doclint.error_correction import (
    ErrorCorrectionHandler,
    DiffOperation,
)
from zh_doclint.error_detection import detect_e101  # noqa
from zh_doclint.error_detection import detect_e102  # noqa

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

    l1 = [True] * (len(h.raw_lines[1]) + 1)
    l1[0] = l1[2] = False
    assert l1 == h.lcs_matrix[1]

    l3 = [True] * (len(h.raw_lines[3]) + 1)
    l3[0] = l3[2] = False
    assert l3 == h.lcs_matrix[3]

    l1 = [1, 3, 4]
    assert l1 == h.index_matrix[1]

    l3 = [1, 3]
    assert l3 == h.index_matrix[3]


def test_coordinate_query():

    h = ErrorCorrectionHandler(SIMPLE_CONTENT, SIMPLE_ELEMENTS)
    q = h.coordinate_query

    assert (1, 1) == q.query(0)
    assert (1, 4) == q.query(2)
    assert (3, 1) == q.query(3)
    assert (3, 3) == q.query(4)

    assert (3, 1) == q.query(0, base_loc=3)
    assert (3, 3) == q.query(1, base_loc=3)

    text = q.text()
    m = re.search(r'(ac)(\s+)(ac)', text)
    assert [
        [(1, 1), (1, 3)],
        [(1, 4)],
        [(3, 1), (3, 3)],
    ] == q.query_match(m)

    text = q.text(2, 3)
    m = re.search(r'(ac)', text)
    assert [
        [(3, 1), (3, 3)],
    ] == q.query_match(m, base_loc=2)

    # empty group.
    text = q.text()
    m = re.search(r'(a)()(c)', text)
    assert [
        [(1, 1)],
        [],
        [(1, 3)],
    ] == q.query_match(m)


def simple_init(error_code, text):
    te = TextElement('', 1, 1, text)
    h = ErrorCorrectionHandler(
        text,
        (te, 'EOF'),
    )
    detector = globals()['detect_{0}'.format(error_code.lower())]
    h(error_code, te, detector(te))
    return h


def test_correct_e101():
    h = simple_init('E101', '中文english')
    assert [DiffOperation.insert(1, 3, val=' ')] == h.diffs

    h = simple_init('E101', 'english中文')
    assert [DiffOperation.insert(1, 8, val=' ')] == h.diffs

    h = simple_init('E101', '中文   english')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.delete(1, 5),
        DiffOperation.insert(1, 6, val=' '),
    ] == h.diffs

    h = simple_init('E101', 'english   中文')
    assert [
        DiffOperation.delete(1, 8),
        DiffOperation.delete(1, 9),
        DiffOperation.delete(1, 10),
        DiffOperation.insert(1, 11, val=' '),
    ] == h.diffs

    h = simple_init('E101', '中文\tenglish')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.insert(1, 4, val=' '),
    ] == h.diffs

    h = simple_init('E101', 'english\t中文')
    assert [
        DiffOperation.delete(1, 8),
        DiffOperation.insert(1, 9, val=' '),
    ] == h.diffs


def test_correct_e102():
    h = simple_init('E102', '中文42')
    assert [DiffOperation.insert(1, 3, val=' ')] == h.diffs

    h = simple_init('E102', '42中文')
    assert [DiffOperation.insert(1, 3, val=' ')] == h.diffs

    h = simple_init('E102', '中文   42')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.delete(1, 5),
        DiffOperation.insert(1, 6, val=' '),
    ] == h.diffs

    h = simple_init('E102', '42   中文')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.delete(1, 5),
        DiffOperation.insert(1, 6, val=' '),
    ] == h.diffs

    h = simple_init('E102', '中文\t42')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.insert(1, 4, val=' '),
    ] == h.diffs

    h = simple_init('E102', '42\t中文')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.insert(1, 4, val=' '),
    ] == h.diffs
