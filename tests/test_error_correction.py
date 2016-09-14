# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re

from zhlint.error_correction import (
    ErrorCorrectionHandler,
    DiffOperation,
    INT_MAX,
)
from zhlint.error_detection import detect_e101  # noqa
from zhlint.error_detection import detect_e102  # noqa
from zhlint.error_detection import detect_e103  # noqa
from zhlint.error_detection import detect_e104  # noqa
from zhlint.error_detection import detect_e201  # noqa
from zhlint.error_detection import detect_e202  # noqa
from zhlint.error_detection import detect_e203  # noqa
from zhlint.error_detection import detect_e204  # noqa
from zhlint.error_detection import detect_e205  # noqa
from zhlint.error_detection import detect_e206  # noqa
from zhlint.error_detection import detect_e207  # noqa
from zhlint.error_detection import detect_e301  # noqa

from zhlint.utils import TextElement


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
    te = TextElement('', 1, 1, text, offset=0)
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


def test_correct_e103():
    h = simple_init('E103', '42μ')
    assert [DiffOperation.insert(1, 3, val=' ')] == h.diffs

    h = simple_init('E103', '42  μ')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.insert(1, 5, val=' '),
    ] == h.diffs


def test_correct_e104():
    h = simple_init('E104', '(42）')
    assert [
        DiffOperation.replace(1, 4, val=')'),
    ] == h.diffs

    h = simple_init('E104', '（42）')
    assert [
        DiffOperation.replace(1, 1, val='('),
        DiffOperation.replace(1, 4, val=')'),
    ] == h.diffs

    h = simple_init('E104', '42(42)')
    assert [
        DiffOperation.insert(1, 3, val=' '),
    ] == h.diffs

    h = simple_init('E104', '42  (42)')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.insert(1, 5, val=' '),
    ] == h.diffs

    h = simple_init('E104', '  (42)')
    assert [
        DiffOperation.delete(1, 1),
        DiffOperation.delete(1, 2),
    ] == h.diffs


def test_correct_e201():
    h = simple_init('E201', '有中文,错误.')
    assert [
        DiffOperation.replace(1, 4, val='，'),
        DiffOperation.replace(1, 7, val='。'),
    ] == h.diffs

    h = simple_init('E201', '有中文, 错误.')
    assert [
        DiffOperation.replace(1, 4, val='，'),
        DiffOperation.delete(1, 5),
        DiffOperation.replace(1, 8, val='。'),
    ] == h.diffs

    h = simple_init('E201', '有中文"错误"')
    assert [
        DiffOperation.replace(1, 4, val='「'),
        DiffOperation.replace(1, 7, val='」'),
    ] == h.diffs

    h = simple_init('E201', '有中文(错误)')
    assert [
        DiffOperation.replace(1, 4, val='（'),
        DiffOperation.replace(1, 7, val='）'),
    ] == h.diffs

    h = simple_init('E201', ' 步的重定向 transitions $$.')
    assert [
        DiffOperation.replace(1, 22, val='。'),
    ] == h.diffs


def test_correct_e202():
    h = simple_init('E202', 'english，test。')
    assert [
        DiffOperation.replace(1, 8, val=', '),
        DiffOperation.replace(1, 13, val='. '),
    ] == h.diffs


def test_correct_e203():
    h = simple_init('E203', '中文， 测试')
    assert [
        DiffOperation.delete(1, 4),
    ] == h.diffs

    h = simple_init('E203', '中文 ，测试')
    assert [
        DiffOperation.delete(1, 3),
    ] == h.diffs


def test_correct_e204():
    h = simple_init('E204', '中文“测试”')
    assert [
        DiffOperation.replace(1, 3, '「'),
        DiffOperation.replace(1, 6, '」'),
    ] == h.diffs

    h = simple_init('E204', '中文‘测试’')
    assert [
        DiffOperation.replace(1, 3, '「'),
        DiffOperation.replace(1, 6, '」'),
    ] == h.diffs


def test_correct_e205():

    h = simple_init('E205', '中文...')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.delete(1, 5),
        DiffOperation.insert(INT_MAX, INT_MAX, '......'),
    ] == h.diffs

    h = simple_init('E205', '中文.......')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.delete(1, 5),
        DiffOperation.delete(1, 6),
        DiffOperation.delete(1, 7),
        DiffOperation.delete(1, 8),
        DiffOperation.delete(1, 9),
        DiffOperation.insert(INT_MAX, INT_MAX, '......'),
    ] == h.diffs

    h = simple_init('E205', '中文。。')
    assert [
        DiffOperation.delete(1, 3),
        DiffOperation.delete(1, 4),
        DiffOperation.insert(INT_MAX, INT_MAX, '......'),
    ] == h.diffs


def test_correct_e206():
    h = simple_init('E206', 'this is sparta!!!')
    assert [
        DiffOperation.delete(1, 15),
        DiffOperation.delete(1, 16),
        DiffOperation.delete(1, 17),
        DiffOperation.insert(INT_MAX, INT_MAX, '!'),
    ] == h.diffs

    h = simple_init('E206', 'this is sparta???')
    assert [
        DiffOperation.delete(1, 15),
        DiffOperation.delete(1, 16),
        DiffOperation.delete(1, 17),
        DiffOperation.insert(INT_MAX, INT_MAX, '?'),
    ] == h.diffs


def test_correct_e207():
    h = simple_init('E207', '讨厌啦~')
    assert [
        DiffOperation.delete(1, 4),
    ] == h.diffs

    h = simple_init('E207', '讨厌啦~~~~')
    assert [
        DiffOperation.delete(1, 4),
        DiffOperation.delete(1, 5),
        DiffOperation.delete(1, 6),
        DiffOperation.delete(1, 7),
    ] == h.diffs


def test_correct_e301():
    h = simple_init('E301', 'APP')
    assert [
        DiffOperation.delete(1, 1),
        DiffOperation.delete(1, 2),
        DiffOperation.delete(1, 3),
        DiffOperation.insert(INT_MAX, INT_MAX, val='App'),
    ] == h.diffs
