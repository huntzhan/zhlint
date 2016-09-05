# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from zh_doclint.preprocessor import TextElement
from zh_doclint.detect_errors import (
    check_e101,
    check_e102,
    check_e103,
    check_e104,
    check_e203,
    check_e205,
)


def test_e101():

    te = TextElement(
        '', '1', '2',
        '中文english',
    )
    assert not check_e101(te)

    te = TextElement(
        '', '1', '2',
        'english中文',
    )
    assert not check_e101(te)

    te = TextElement(
        '', '1', '2',
        '中文  english',
    )
    assert not check_e101(te)

    te = TextElement(
        '', '1', '2',
        'english  中文',
    )
    assert not check_e101(te)

    te = TextElement(
        '', '1', '2',
        '中文\tenglish',
    )
    assert not check_e101(te)

    te = TextElement(
        '', '1', '2',
        '中文 english',
    )
    assert check_e101(te)

    te = TextElement(
        '', '1', '2',
        'english 中文',
    )
    assert check_e101(te)

    te = TextElement(
        '', '1', '2',
        '中文\nenglish',
    )
    assert check_e101(te)

    te = TextElement(
        '', '1', '2',
        '42\n中文',
    )
    assert check_e102(te)


def test_e102():

    te = TextElement(
        '', '1', '2',
        '中文1',
    )
    assert not check_e102(te)

    te = TextElement(
        '', '1', '2',
        '42中文',
    )
    assert not check_e102(te)

    te = TextElement(
        '', '1', '2',
        '中文  42',
    )
    assert not check_e102(te)

    te = TextElement(
        '', '1', '2',
        '42  中文',
    )
    assert not check_e102(te)

    te = TextElement(
        '', '1', '2',
        '中文\t42',
    )
    assert not check_e102(te)

    te = TextElement(
        '', '1', '2',
        '中文 42',
    )
    assert check_e102(te)

    te = TextElement(
        '', '1', '2',
        '42 中文',
    )
    assert check_e102(te)

    te = TextElement(
        '', '1', '2',
        '中文\n42',
    )
    assert check_e102(te)

    te = TextElement(
        '', '1', '2',
        '42\n中文',
    )
    assert check_e102(te)


def test_e103():

    te = TextElement(
        '', '1', '2',
        'μ42',
    )
    assert not check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42μ',
    )
    assert not check_e103(te)

    te = TextElement(
        '', '1', '2',
        'μ  42',
    )
    assert not check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42  μ',
    )
    assert not check_e103(te)

    te = TextElement(
        '', '1', '2',
        'μ\t42',
    )
    assert not check_e103(te)

    te = TextElement(
        '', '1', '2',
        'μ 42',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42 μ',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        'μ\n42',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42\nμ',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42x',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42n',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42％',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42%',
    )
    assert check_e103(te)

    te = TextElement(
        '', '1', '2',
        '42℃',
    )
    assert check_e103(te)


def test_e104():

    te = TextElement(
        '', '1', '2',
        '(42）',
    )
    assert not check_e104(te)

    te = TextElement(
        '', '1', '2',
        '（42)',
    )
    assert not check_e104(te)

    te = TextElement(
        '', '1', '2',
        '（42）',
    )
    assert not check_e104(te)

    te = TextElement(
        '', '1', '2',
        '42(42)',
    )
    assert not check_e104(te)

    te = TextElement(
        '', '1', '2',
        '42  (42)',
    )
    assert not check_e104(te)

    te = TextElement(
        '', '1', '2',
        '42 (42)',
    )
    assert check_e104(te)

    te = TextElement(
        '', '1', '2',
        '42\n(42)',
    )
    assert check_e104(te)


def test_e203():

    te = TextElement(
        '', '1', '2',
        '中文， 测试',
    )
    assert not check_e203(te)

    te = TextElement(
        '', '1', '2',
        '中文 。测试',
    )
    assert not check_e203(te)

    te = TextElement(
        '', '1', '2',
        '「 中文」',
    )
    assert not check_e203(te)

    te = TextElement(
        '', '1', '2',
        '中文，测试',
    )
    assert check_e203(te)

    te = TextElement(
        '', '1', '2',
        '中文；测试',
    )
    assert check_e203(te)

    te = TextElement(
        '', '1', '2',
        '「中文」',
    )
    assert check_e203(te)

    te = TextElement(
        '', '1', '2',
        '中文！\n测试',
    )
    assert check_e203(te)


def test_e205():

    te = TextElement(
        '', '1', '2',
        '中文...',
    )
    assert not check_e205(te)

    te = TextElement(
        '', '1', '2',
        '中文.......',
    )
    assert not check_e205(te)

    te = TextElement(
        '', '1', '2',
        '中文。。。',
    )
    assert not check_e205(te)

    te = TextElement(
        '', '1', '2',
        '中文......',
    )
    assert check_e205(te)
