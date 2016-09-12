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

from zhlint.utils import (
    TextElement,
    count_newlines,
    count_offset,
    try_invoke
)


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


# 1: a.
# 2: whitespaces.
# 3: b.
def single_space_patterns(a, b, a_join_b=True, b_join_a=True):

    # 1. no space.
    # prefix check.
    p11 = r'({0})()({1})'
    # suffix check.
    p12 = r'({1})()({0})'

    # 2. more than one whitespaces.
    # prefix check.
    p21 = (
        r'({0})'
        r'((?:(?!\n)\s){{2,}})'
        r'({1})'
    )
    # suffix check.
    p22 = (
        r'({1})'
        r'((?:(?!\n)\s){{2,}})'
        r'({0})'
    )

    # 3. wrong single whitespace: [\t\r\f\v]
    # only allow ' ' and '\n'.
    # prefix check.
    p31 = (
        r'({0})'
        r'((?:(?![ \n])\s){{1}})'
        r'({1})'
    )
    # suffix check.
    p32 = (
        r'({1})'
        r'((?:(?![ \n])\s){{1}})'
        r'({0})'
    )

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


# 1: a.
# 2: whitespaces.
# 3: b.
def no_space_patterns(a, b):

    # prefix check.
    p1 = (
        r'({0})'
        r'((?:(?!\n)\s)+)'
        r'({1})'
    )
    # suffix check.
    p2 = (
        r'({1})'
        r'((?:(?!\n)\s)+)'
        r'({0})'
    )

    return list(map(
        methodcaller('format', a, b),
        [p1, p2],
    ))


def detect_by_patterns(patterns, element, ignore_matches=set()):

    for pattern in patterns:
        for m in re.finditer(pattern, element.content, re.UNICODE):
            if m.group(0) in ignore_matches:
                continue
            yield m


def detect_e101(element):

    return detect_by_patterns(
        single_space_patterns(ZH_CHARACTERS, r'[a-zA-z]'),
        element,
    )


def detect_e102(element):

    return detect_by_patterns(
        single_space_patterns(ZH_CHARACTERS, r'\d'),
        element,
    )


def detect_e103(element):

    p = (
        # non-digit, non-chinese
        r'(?:(?!\d|{0}|{1}|[!-/:-@\[-`{{-~]|\s))'
        # ignore ％, ℃, x, n.
        r'[^\uff05\u2103xn\%]'
    )
    p = p.format(ZH_CHARACTERS, ZH_SYMBOLS)

    return detect_by_patterns(
        single_space_patterns(
            r'\d',
            p,
            b_join_a=False,
        ),
        element,
    )


# 1: whitespaces.
# 2: left parenthesis.
# 3: digits.
# 4: right parenthesis.
def detect_e104(element):

    p1 = (
        r'(?<=[^\s]{1})'
        r'(\s*)'
        r'([(\uff08])'
        r'(\d+)'
        r'([)\uff09])'
    )

    # cover
    p2 = (
        r'(?:^|\n)'
        r'(\s*)'
        r'([(\uff08])'
        r'(\d+)'
        r'([)\uff09])'
    )

    patterns = [p1, p2]
    for i, p in enumerate(patterns):
        for m in detect_by_patterns([p], element):
            yield_tag = None
            if m.group(2) != '(' or m.group(4) != ')':
                yield_tag = 0
            # preceded by non-whitespace.
            if i == 0 and m.group(1) not in (' ', '\n'):
                yield_tag = 1
            # preceded by nothing or newline.
            if i == 1 and m.group(1) != '':
                yield_tag = 2

            if yield_tag is not None:
                yield m, yield_tag


def detect_e203(element):

    return detect_by_patterns(
        no_space_patterns(
            ZH_SYMBOLS,
            r'(?:(?!{0}|\s)).'.format(ZH_SYMBOLS),
        ),
        element,
    )


# 1: ellipsis.
def detect_e205(element):

    p = r'(\.{2,}|。{2,})'
    for m in re.finditer(p, element.content, flags=re.UNICODE):
        detected = m.group(0)
        if detected[0] != '.' or len(detected) != 6:
            yield m


# 1: duplicated marks.
def detect_e206(element):

    p1 = r'([!！]{2,})'
    p2 = r'([?？]{2,})'

    return detect_by_patterns(
        [p1, p2],
        element,
    )


# 1: ~
def detect_e207(element):

    p1 = r'(~+)'

    return detect_by_patterns(
        [p1],
        element,
    )


def contains_chinese_characters(content):
    return re.search(ZH_CHARACTERS, content, re.UNICODE)


# 1: en punctuations.
# 2: whitespaces.
def detect_e201(element):
    if not contains_chinese_characters(element.content):
        return False

    PUNCTUATIONS = set('!"$\'(),.:;<>?[\\]^_{}/')

    def marks_pattern(pattern_template, texts):

        patterns = []
        for text in texts:
            pattern = r'({0})'.format(re.escape(text))
            patterns.append(pattern)

        return pattern_template.format(r'|'.join(patterns))

    def split_by_e104(te):
        return [
            TextElement(te.block_type, te.loc_begin, te.loc_end, content)
            for content in re.split(r'\(\d+\)', te.content, flags=re.UNICODE)
        ]

    LATEX_MARKS = ['$$', '\(', '\)']

    ret = []

    # gerneral forms, ignore common shared characters: '@#%&+*-=|~'
    p1 = r'([{0}]+)(\s*)'.format(re.escape(''.join(PUNCTUATIONS)))

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

    patterns = [p1, p2, p3, p4, p5]

    for element in split_by_e104(element):
        for m in detect_by_patterns(
            patterns,
            element,
            ignore_matches=set(['......']),
        ):
            if SpecialWordHelper.delimiter_in_word(element.content, m):
                continue

            contains_mark = False
            for mark in LATEX_MARKS:
                if mark in m.group(0):
                    contains_mark = True
                    break
            if not contains_mark:
                ret.append(m)

    return ret


# 1: chineses.
def detect_e202(element):
    if contains_chinese_characters(element.content):
        return False

    return detect_by_patterns(
        ['({0})'.format(ZH_SYMBOLS)],
        element,
    )


# 1: wrong 「」.
def detect_e204(element):
    if not contains_chinese_characters(element.content):
        return False

    p = (
        r'('

        # ', " is handled by E201.
        # r"'"
        # r'|'
        # r'"'
        # r'|'

        # ‘’
        r'\u2018|\u2019'
        r'|'
        # “”
        r'\u201c|\u201d'

        r')'
    )
    return detect_by_patterns(
        [p],
        element,
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
        delimiter = match.group(1)
        if delimiter not in cls.SENTENCE_DELIMITER_TO_WORD:
            return False

        segment = cls.select_segment(content, match)
        for word in cls.SENTENCE_DELIMITER_TO_WORD.get(delimiter, []):
            if segment.find(word) >= 0:
                return True
        return False


SpecialWordHelper.init()


# 1: wrong special word.
def detect_e301(element):

    for correct_form, pattern in SpecialWordHelper.WORD_PATTERN.items():

        # (?<!xxx) and (?!xxx) could match ^ and $.
        p = r'(?<![a-zA-Z])({0})(?![a-zA-Z])'.format(pattern)

        for m in re.finditer(
            p, element.content,
            flags=re.UNICODE | re.IGNORECASE,
        ):
            if m.group(0) != correct_form:
                yield m, correct_form


def process_errors_by_handler(error_codes, error_handler, element):

    for error_code in error_codes:
        detector = globals()['detect_{0}'.format(error_code.lower())]
        error_handler(error_code, element, detector(element))


def process_block_level_errors(error_handler, element):

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
        element,
    )


def split_text_element(element):

    # block_type should be split by newline first.
    SPLIT_BY_NEWLINES = [
        'list_block',
        'table',
    ]

    elements = []
    if element.block_type not in SPLIT_BY_NEWLINES:
        elements.append(element)
    else:
        content = element.content
        loc_begin = element.loc_begin

        if not content.strip('\n'):
            return []
        else:
            content = content.strip('\n')
            for line in content.split('\n'):
                elements.append(
                    TextElement(
                        'paragraph',
                        loc_begin, loc_begin,
                        line,
                    )
                )
                loc_begin += 1

    # split sentences.
    SENTENCE_DELIMITERS = (
        r'('
        r'\.{6}'
        r'|'
        r'!|;|\.|\?'
        r'|'
        r'\uff01|\uff1b|\u3002|\uff1f'
        r')'
    )

    OPEN_PARENTHESIS = set(
        '('
        '['
        "'"
        '"'
        '（'
        '「'
        '『'
    )
    CLOSE_PARENTHESIS = set(
        ')'
        ']'
        "'"
        '"'
        '）'
        '」'
        '』'
    )

    sentences = []

    for element in elements:
        content = element.content.strip('\n')

        loc_begin = element.loc_begin
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

            level = 0
            for c in sentence:
                if c in OPEN_PARENTHESIS:
                    level += 1
                elif c in CLOSE_PARENTHESIS:
                    level -= 1
            if level != 0:
                continue

            newlines = count_newlines(sentence)
            offset = count_offset(content[:sbegin])

            sentences.append(
                TextElement(
                    'paragraph',
                    loc_begin,
                    loc_begin + newlines - tailing_newlines,
                    sentence,
                    offset=offset,
                )
            )

            loc_begin += newlines
            sbegin = send

        if sbegin < len(content):
            sentences.append(
                TextElement(
                    'paragraph',
                    loc_begin, loc_begin,
                    content[sbegin:],
                    offset=count_offset(content[:sbegin]),
                )
            )
    return sentences


def process_sentence_level_errors(error_handler, element):

    process_errors_by_handler(
        [
            'E201',
            'E202',
            'E204',
        ],
        error_handler,
        element,
    )


def process_errors(error_handler, element):

    try_invoke(error_handler, 'before_block_level')
    process_block_level_errors(error_handler, element),
    try_invoke(error_handler, 'after_block_level')

    try_invoke(error_handler, 'before_sentence_level')
    for sentence in split_text_element(element):
        process_sentence_level_errors(error_handler, sentence)
    try_invoke(error_handler, 'after_sentence_level')
