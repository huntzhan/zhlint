# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from zh_doclint.preprocessor import TextElement
from zh_doclint.detect_errors import (
    check_e101,
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
        'english\n中文',
    )
    assert check_e101(te)
