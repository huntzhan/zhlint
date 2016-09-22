# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from operator import attrgetter

from zhlint.utils import TextElement
from zhlint.error_detection import (
    detect_e101,
    detect_e102,
    detect_e103,
    detect_e104,
    detect_e203,
    detect_e205,
    detect_e206,
    detect_e207,
    detect_e301,

    detect_e201,
    detect_e202,
    detect_e204,

    split_text_element,
)


def check_texts(inputs, detector, should_detected):
    elements = []

    for i in inputs:
        if isinstance(i, str):
            elements.append(
                TextElement('', '1', '2', i)
            )
        elif isinstance(i, TextElement):
            elements.append(i)
        else:
            raise RuntimeError

    for element in elements:
        matches = detector(element)
        if should_detected:
            assert matches
            assert list(matches)
        else:
            assert not matches or not list(matches)


def test_e101():

    check_texts(
        [
            '中文english',
            'english中文',
            '中文  english',
            'english  中文',
            '中文\tenglish',
        ],
        detect_e101,
        should_detected=True,
    )

    check_texts(
        [
            '中文 english',
            'english 中文',
            '中文\nenglish',
            '42\n中文',
        ],
        detect_e101,
        should_detected=False,
    )


def test_e102():

    check_texts(
        [
            '中文1',
            '42中文',
            '中文  42',
            '42  中文',
            '中文\t42',
        ],
        detect_e102,
        should_detected=True,
    )

    check_texts(
        [
            '中文 42',
            '42 中文',
            '中文\n42',
            '中文 \n42',
            '42\n中文',
        ],
        detect_e102,
        should_detected=False,
    )


def test_e103():

    check_texts(
        [
            '42μ',
            '42  μ',
        ],
        detect_e103,
        should_detected=True,
    )

    check_texts(
        [
            '42 μ',
            'μ\n42',
            '42\nμ',
            '42x',
            '42n',
            '42％',
            '42%',
            '42℃',
            '，42',
            '42。',
            'Q3',
            '136-4321-1234',
            'word2vec',
            'word20000vec',
        ],
        detect_e103,
        should_detected=False,
    )


def test_e104():

    check_texts(
        [
            '(42）',
            '（42)',
            '（42）',
            '42(42)',
            '42  (42)',
            ' (42)',
        ],
        detect_e104,
        should_detected=True,
    )

    check_texts(
        [
            '42 (42)',
            '42\n(42)',
            '(42)',
        ],
        detect_e104,
        should_detected=False,
    )


def test_e203():

    check_texts(
        [
            '中文， 测试',
            '中文 。测试',
            '「 中文」',
        ],
        detect_e203,
        should_detected=True,
    )

    check_texts(
        [
            '中文，测试',
            '中文；测试',
            '「中文」',
            '中文！\n测试',
        ],
        detect_e203,
        should_detected=False,
    )


def test_e205():

    check_texts(
        [
            '中文...',
            '中文.......',
            '中文。。。',
        ],
        detect_e205,
        should_detected=True,
    )

    check_texts(
        [
            '中文......',
            '中文 test@email.com',
            '中文 +135-1234-5678'
            '中文 (1) '
        ],
        detect_e205,
        should_detected=False,
    )


def test_e206():

    check_texts(
        [
            '中文!!',
            '中文！！',
            '中文!！',
            '中文??',
            '中文？？',
            '中文？?',
        ],
        detect_e206,
        should_detected=True,
    )

    check_texts(
        [
            '中文!',
            '中文！',
            '中文?',
            '中文？',
            'english, with space',
        ],
        detect_e206,
        should_detected=False,
    )


def test_e207():

    check_texts(
        [
            '中文~',
        ],
        detect_e207,
        should_detected=True,
    )

    check_texts(
        [
            '中文',
        ],
        detect_e207,
        should_detected=False,
    )


def test_e301():

    check_texts(
        [
            'APP',
            'app',
            'android',
            'ios',
            'IOS',
            'IPHONE',
            'iphone',
            'AppStore',
            'app store',
            'wifi',
            'Wifi',
            'Wi-fi',
            'E-mail',
            'Email',
            'PS',
            'ps',
            'Ps.',

            '我app store我',
        ],
        detect_e301,
        should_detected=True,
    )


def test_e201():

    check_texts(
        [
            '有中文, 错误.',
            'LaTeX 公式 $$.',
            'LaTeX 公式,$$',
            'LaTeX 公式 \(\).',
            'LaTeX 公式,\(\)',
        ],
        detect_e201,
        should_detected=True,
    )

    check_texts(
        [
            '有中文，正确。',
            '有中文，正确......',
            'pure english, nothing wrong.',
            'P.S. 这是一行中文。',
            'LaTeX 公式 $$',
            'LaTeX 公式 \(\)',
            '邮箱：programmer.zhx@gmail.com',
            '1.0',
            'www.google.com',
            '链接地址 http://google.com',
        ],
        detect_e201,
        should_detected=False,
    )


def test_e202():

    check_texts(
        [
            'pure english，nothing wrong.',
        ],
        detect_e202,
        should_detected=True,
    )

    check_texts(
        [
            'pure english, nothing wrong.',
        ],
        detect_e202,
        should_detected=False,
    )


def test_e204():

    check_texts(
        [
            # "中文'测试'",
            # '中文"测试"',
            '中文‘测试’',
            '中文“测试”',
        ],
        detect_e204,
        should_detected=True,
    )

    check_texts(
        [
            "中文「测试」",
        ],
        detect_e204,
        should_detected=False,
    )


def test_split_text_element():

    def access(key, te):
        return list(map(attrgetter(key), split_text_element(te)))

    def help_(content, begin, end):
        te = TextElement(
            'paragraph', begin, end,
            content,
        )

        lines = access('content', te)
        begins = access('loc_begin', te)
        ends = access('loc_end', te)
        offsets = access('offset', te)

        return lines, begins, ends, offsets

    content = '''a
b.
c. inline!
d
e.'''

    lines, begins, ends, offsets = help_(content, '1', '5')

    assert ['a\nb.\n', 'c.', ' inline!\n', 'd\ne.'] == lines
    assert [1, 3, 3, 4] == begins
    assert [2, 3, 3, 5] == ends
    assert [0, 0, 2, 0] == offsets

    content = '''a......
b!
c;
d.
e?
f！
g；
h。
i？'''

    lines, begins, ends, offsets = help_(content, '1', '9')
    assert len(lines) == 9

    content = '''P.S. this is a line!'''

    lines, begins, ends, offsets = help_(content, '1', '9')
    assert len(lines) == 1

    content = '''邮箱：abc.de@fgh.com！'''

    lines, begins, ends, offsets = help_(content, '1', '9')
    assert len(lines) == 1

    content = '''sentence 1.
   （中文！中文！）
sentence 2.'''
    lines, begins, ends, offsets = help_(content, '1', '3')

    assert ['sentence 1.\n', '   （中文！中文！）\nsentence 2.'] == lines
    assert [1, 2] == begins
    assert [1, 3] == ends
    assert [0, 0] == offsets

    content = '''sentence 1.
sentence 2.  sentence 3'''
    lines, begins, ends, offsets = help_(content, '1', '2')

    assert ['sentence 1.\n', 'sentence 2.', '  sentence 3'] == lines
    assert [1, 2, 2] == begins
    assert [1, 2, 2] == ends
    assert [0, 0, 11] == offsets
