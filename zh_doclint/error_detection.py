# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re
from operator import methodcaller
from collections import defaultdict
import itertools

from zh_doclint.preprocessor import TextElement


ZH_CHARACTERS = (
    r'[\u4e00-\u9fff]'
)

ZH_SYMBOLS = (
    r'['
    r'\u3000-\u303f'
    r'\uff00-\uff0f'
    r'\uff1a-\uff20'
    r'\uff3b-\uff40'
    r'\uff5b-\uff64'
    r'\uffe0-\uffee'
    r']'
)


def single_space_patterns(a, b, a_join_b=True, b_join_a=True):

    # 1. no space.
    # prefix check.
    p11 = r'{0}{1}'
    # suffix check.
    p12 = r'{1}{0}'

    # 2. more than one whitespaces.
    # prefix check.
    p21 = r'{0}((?!\n)\s){{2,}}{1}'
    # suffix check.
    p22 = r'{1}((?!\n)\s){{2,}}{0}'

    # 3. wrong single whitespace: [\t\r\f\v]
    # only allow ' ' and '\n'.
    # prefix check.
    p31 = r'{0}(?![ \n])\s{{1}}{1}'
    # suffix check.
    p32 = r'{1}(?![ \n])\s{{1}}{0}'

    patterns = []
    if a_join_b:
        patterns.extend([
            p11,
            p21,
            p31,
        ])
    if b_join_a:
        patterns.extend([
            p12,
            p22,
            p32,
        ])

    return list(map(
        methodcaller('format', a, b),
        patterns,
    ))


def no_space_patterns(a, b):

    # prefix check.
    p1 = r'{0}((?!\n)\s)+{1}'
    # suffix check.
    p2 = r'{1}((?!\n)\s)+{0}'

    return list(map(
        methodcaller('format', a, b),
        [p1, p2],
    ))


def detect_by_patterns(patterns, text_element, ignore_matches=set()):

    for pattern in patterns:
        for m in re.finditer(pattern, text_element.content, re.UNICODE):
            if m.group(0) in ignore_matches:
                continue
            yield m


def detect_e101(text_element):

    return detect_by_patterns(
        single_space_patterns(ZH_CHARACTERS, r'[a-zA-z]'),
        text_element,
    )


def detect_e102(text_element):

    return detect_by_patterns(
        single_space_patterns(ZH_CHARACTERS, r'\d'),
        text_element,
    )


def detect_e103(text_element):

    return detect_by_patterns(
        single_space_patterns(
            r'\d',
            # non-digit, non-chinese, ％, ℃, x, n.
            r'(?!\d|{0}|{1}|[!-/:-@\[-`{{-~]|\s)[^\uff05\u2103xn\%]'.format(
                ZH_CHARACTERS, ZH_SYMBOLS,
            ),
            b_join_a=False,
        ),
        text_element,
    )


def detect_e104(text_element):

    pattern = (
        r'(\s*)'
        r'([(\uff08])'
        r'\d+'
        r'([)\uff09])'
    )

    content = text_element.content

    for m in re.finditer(pattern, content, flags=re.UNICODE):
        if m.group(2) != '(' or m.group(3) != ')':
            yield m
        if m.group(1) not in (' ', '\n'):
            yield m


def detect_e203(text_element):

    return detect_by_patterns(
        no_space_patterns(
            ZH_SYMBOLS,
            r'(?!{0}|\s).'.format(ZH_SYMBOLS),
        ),
        text_element,
    )


def detect_e205(text_element):

    p = r'\.{2,}|。{2,}'
    for m in re.finditer(p, text_element.content, flags=re.UNICODE):
        detected = m.group(0)
        if detected[0] != '.' or len(detected) != 6:
            yield m


def detect_e206(text_element):

    p1 = r'!{2,}'
    p2 = r'！{2,}'

    return detect_by_patterns(
        [p1, p2],
        text_element,
    )


def detect_e207(text_element):

    p1 = r'~+'

    return detect_by_patterns(
        [p1],
        text_element,
    )


def contains_chinese_characters(content):
    return re.search(ZH_CHARACTERS, content, re.UNICODE)


def detect_e201(text_element):
    if not contains_chinese_characters(text_element.content):
        return False

    PUNCTUATIONS = set('!"$\'(),.:;<>?[\\]^_{}')

    def marks_pattern(pattern_template, texts):

        patterns = []
        for text in texts:
            pattern = r'({0})'.format(re.escape(text))
            patterns.append(pattern)

        return pattern_template.format(r'|'.join(patterns))

    LATEX_MARKS = ['$$', '\(', '\)']

    ret = []

    # gerneral forms, ignore common shared characters: '@#%&+*-=|~'
    p1 = r'[{0}]+'.format(re.escape(''.join(PUNCTUATIONS)))

    # prefix
    p2 = ''.join(itertools.chain(
        marks_pattern(r'(?<={0})', LATEX_MARKS),
        p1,
    ))
    # suffix.
    p3 = ''.join(itertools.chain(
        p1,
        marks_pattern(r'(?={0})', LATEX_MARKS),
    ))
    # special cases: \(\).
    p4 = ''.join(itertools.chain(
        marks_pattern(r'(?<={0})', ['\(\)']),
        p1,
    ))
    # suffix.
    p5 = ''.join(itertools.chain(
        p1,
        marks_pattern(r'(?={0})', ['\(\)']),
    ))

    for m in detect_by_patterns(
        [p1, p2, p3, p4, p5],
        text_element,
        ignore_matches=set(['......']),
    ):
        if SpecialWordHelper.delimiter_in_word(text_element.content, m):
            continue

        contains_mark = False
        for mark in LATEX_MARKS:
            if mark in m.group(0):
                contains_mark = True
                break
        if not contains_mark:
            ret.append(m)

    return ret


def detect_e202(text_element):
    if contains_chinese_characters(text_element.content):
        return False

    return detect_by_patterns(
        [ZH_SYMBOLS],
        text_element,
    )


def detect_e204(text_element):
    if not contains_chinese_characters(text_element.content):
        return False

    p = (
        r"'"
        r'|'
        r'"'
        r'|'
        # ‘’
        r'\u2018|\u2019'
        r'|'
        # “”
        r'\u201c|\u201d'
    )
    return detect_by_patterns(
        [p],
        text_element,
    )


class SpecialWordHelper(object):

    WORD_PATTERN = {
        'App': r'app',
        'Android': r'android',
        'iOS': r'ios',
        'iPhone': r'iphone',
        'App Store': r'app\s?store',
        'WiFi': r'wi-*fi',
        'email': r'e-*mail',
        'P.S.': r'P\.*S\.*',
    }

    WORD_MAX_LENGTH = None
    SENTENCE_DELIMITER_TO_WORD = None

    @classmethod
    def init(cls):
        if cls.WORD_MAX_LENGTH and cls.SENTENCE_DELIMITER_TO_WORD:
            return

        delimiters = [
            '!', ';', '.', '?',
            '\uff01', '\uff1b', '\u3002', '\uff1f',
        ]

        cls.SENTENCE_DELIMITER_TO_WORD = defaultdict(list)
        for delimiter in delimiters:
            for word in cls.WORD_PATTERN:
                if delimiter not in word:
                    continue
                cls.SENTENCE_DELIMITER_TO_WORD[delimiter].append(word)

        cls.WORD_MAX_LENGTH = 0
        for word in cls.WORD_PATTERN:
            cls.WORD_MAX_LENGTH = max(cls.WORD_MAX_LENGTH, len(word))

    @classmethod
    def select_segment(cls, content, match):
        segment_begin = max(
            0,
            match.end() - SpecialWordHelper.WORD_MAX_LENGTH,
        )
        segment_end = min(
            len(content) - 1,
            match.start() + SpecialWordHelper.WORD_MAX_LENGTH,
        )
        return content[segment_begin:segment_end]

    @classmethod
    def delimiter_in_word(cls, content, match):
        delimiter = match.group(0)
        if delimiter not in cls.SENTENCE_DELIMITER_TO_WORD:
            return False

        segment = cls.select_segment(content, match)
        for word in cls.SENTENCE_DELIMITER_TO_WORD.get(delimiter, []):
            if segment.find(word) >= 0:
                return True
        return False


SpecialWordHelper.init()


def detect_e301(text_element):

    for correct_form, pattern in SpecialWordHelper.WORD_PATTERN.items():

        p1 = r'(?<![a-zA-Z]){0}(?![a-zA-Z])'.format(pattern)
        p2 = r'^{0}(?![a-zA-Z])'.format(pattern)
        p3 = r'(?<![a-zA-Z]){0}$'.format(pattern)

        for p in [p1, p2, p3]:
            for m in re.finditer(
                p, text_element.content,
                flags=re.UNICODE | re.IGNORECASE,
            ):
                if m.group(0) != correct_form:
                    yield m


def process_errors_by_handler(error_codes, error_handler, text_element):

    for error_code in error_codes:
        detector = globals()['detect_{0}'.format(error_code.lower())]
        error_handler(error_code, text_element, detector(text_element))


def process_block_level_errors(error_handler, text_element):

    process_errors_by_handler(
        [
            'E101',
            'E102',
            'E103',
            'E104',

            'E203',
            'E205',
            'E206',
            'E207',

            'E301',
        ],
        error_handler,
        text_element,
    )


def split_text_element(text_element):

    # block_type should be split by newline first.
    SPLIT_BY_NEWLINES = [
        'list_block',
        'table',
    ]

    elements = []
    if text_element.block_type not in SPLIT_BY_NEWLINES:
        elements.append(text_element)
    else:
        content = text_element.content
        loc_begin = int(text_element.loc_begin)

        if not content.strip('\n'):
            return []
        else:
            content = content.strip('\n')
            for line in content.split('\n'):
                elements.append(
                    TextElement(
                        'paragraph',
                        str(loc_begin), str(loc_begin),
                        line,
                    )
                )
                loc_begin += 1

    # split sentences.
    SENTENCE_DELIMITERS = (
        r'\.{6}'
        r'|'
        r'!|;|\.|\?'
        r'|'
        r'\uff01|\uff1b|\u3002|\uff1f'
    )
    sentences = []
    for element in elements:
        content = element.content.strip('\n')

        loc_begin = int(element.loc_begin)
        sbegin = 0

        for m in re.finditer(SENTENCE_DELIMITERS, content, flags=re.UNICODE):
            # ignore delimiter within special words.
            if SpecialWordHelper.delimiter_in_word(content, m):
                continue

            send = m.end()
            tailing_newlines = 0
            while send < len(content) and content[send] == '\n':
                send += 1
                tailing_newlines += 1

            sentence = content[sbegin:send]
            newlines = len(list(filter(lambda c: c == '\n', sentence)))

            sentences.append(
                TextElement(
                    'paragraph',
                    str(loc_begin),
                    str(loc_begin + newlines - tailing_newlines),
                    sentence,
                )
            )

            loc_begin += newlines
            sbegin = send

        if sbegin < len(content):
            sentences.append(
                TextElement(
                    'paragraph',
                    str(loc_begin), str(loc_begin),
                    content[sbegin:],
                )
            )
    return sentences


def process_sentence_level_errors(error_handler, text_element):

    process_errors_by_handler(
        [
            'E201',
            'E202',
            'E204',
        ],
        error_handler,
        text_element,
    )


def process_errors(error_handler, text_element):
    process_block_level_errors(error_handler, text_element),
    for sentence in split_text_element(text_element):
        process_sentence_level_errors(error_handler, sentence)
