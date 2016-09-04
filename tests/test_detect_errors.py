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
