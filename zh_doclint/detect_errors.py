# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re
from operator import methodcaller

import click

from zh_doclint.preprocessor import TextElement


ERRORS = {
    # space.
    'E101': '英文与非标点的中文之间需要有一个空格',
    'E102': '数字与非标点的中文之间需要有一个空格',
    'E103': '除了「％」、「°C」、以及倍数单位（如 2x、3n）之外，'
            '其余数字与单位之间需要加空格',
    'E104': '书写时括号中全为数字，则括号用半角括号且首括号前要空一格',

    # punctuation.
    'E201': '只有中文或中英文混排中，一律使用中文全角标点',
    'E202': '如果出现整句英文，则在这句英文中使用英文、半角标点',
    'E203': '中文标点与其他字符间一律不加空格',
    'E204': '中文文案中使用中文引号「」和『』，其中「」为外层引号',
    'E205': '省略号请使用「……」标准用法',
    'E206': '感叹号请使用「！」标准用法',
    'E207': '请勿在文章内使用「~」',

    # terminology.
    'E301': '常用名词错误',
}

ZH_CHARACTERS = (
    '[\u4e00-\u9fff]'
)

ZH_SYMBOLS = (
    '['
    '\u3000-\u303f'
    '\uff00-\uff0f'
    '\uff1a-\uff20'
    '\uff3b-\uff40'
    '\uff5b-\uff64'
    '\uffe0-\uffee'
    ']'
)


def split_bar(symbol, offset, *texts):
    length = offset
    for text in texts:
        for c in text:
            if 0 <= ord(c) <= 127:
                length += 1
            else:
                length += 2
    length = int(length)

    return click.style(symbol * length)


def error_code(func):

    code = func.__name__[-4:].upper()

    def display(body):
        header = [
            split_bar('=', 2, code, ERRORS[code]),
            click.style('\n'),
            click.style(code, fg='green', bold=True),
            click.style(': '),
            click.style(ERRORS[code]),
            click.style('\n'),
            split_bar('=', 2, code, ERRORS[code]),
            click.style('\n'),
        ]
        for style in header + body:
            click.echo(style, nl=False)
        click.echo('\n', nl=False)

    def wrapper(text_element):

        body = func(text_element)
        if body:
            display(body)
            return False
        return True

    return wrapper


def check_on_callback(callback, text_element):

    def get_loc(i, j):
        begin = int(text_element.loc_begin)
        begin += len(list(filter(
            lambda c: c == '\n', text_element.content[:i],
        )))
        end = begin + len(list(filter(
            lambda c: c == '\n', text_element.content[i:j],
        )))
        return begin, end

    def generate_detected_text(i, j):
        OFFSET = 5
        content = text_element.content

        ri = i
        c = 0
        while ri >= 0 and c < OFFSET and content[ri] != '\n':
            ri -= 1
            c += 1
        ri = min(ri + 1, i)

        rj = j
        c = 0
        while rj < len(content) and c < OFFSET and content[ri] != '\n':
            rj += 1
            c += 1
        rj = max(rj - 1, j)

        text_line = content[ri:rj]
        i = i - ri
        j = j - ri

        for c in ['\t', '\n']:
            for m in re.finditer(c, text_line):
                ci = m.start()
                if ci < i:
                    i += 5
                    j += 5
                elif ci < j:
                    j += 5

            text_line = text_line.replace(
                c,
                ' [{0}] '.format(repr(c)[2:-1]),
            )

        mark_line = []
        for c in text_line[:i]:
            if 0 <= ord(c) <= 127:
                mark_line.append(' ')
            else:
                mark_line.append('\u3000')
        for c in text_line[i:j]:
            if 0 <= ord(c) <= 127:
                mark_line.append('-')
            else:
                mark_line.append('\uff0d')
        mark_line = ''.join(mark_line)

        return text_line, mark_line

    loc_detected = []
    for i, j in callback(text_element):
        loc_detected.append(
            (i, j),
        )

    if not loc_detected:
        return False
    else:
        styles = []
        for i, j in sorted(loc_detected):
            loc = get_loc(i, j)
            text_line, mark_line = generate_detected_text(i, j)

            if loc[0] == loc[1]:
                loc_text = str(loc[0])
            else:
                loc_text = '{0}-{1}'.format(*map(str, loc))

            styles.extend([
                click.style('LINE', fg='green', bold=True),
                click.style(': ', fg='white'),
                click.style(loc_text, fg='red'),
                click.style('\n'),
                click.style(text_line, fg='yellow'),
                click.style('\n'),
                click.style(mark_line, fg='red', bold=True),
                click.style('\n'),
                split_bar('.', 0, text_line),
                click.style('\n'),
            ])
        return styles


def check_on_patterns(patterns, text_element):

    def patterns_callback(text_element):

        for pattern in patterns:
            for m in re.finditer(pattern, text_element.content, re.UNICODE):
                yield m.start(), m.end()

    return check_on_callback(patterns_callback, text_element)


def single_space_patterns(a, b, a_join_b=True, b_join_a=True):

    # 1. no space.
    # prefix check.
    p11 = '{0}{1}'
    # suffix check.
    p12 = '{1}{0}'

    # 2. more than one whitespaces.
    # prefix check.
    p21 = '{0}((?!\n)\s){{2,}}{1}'
    # suffix check.
    p22 = '{1}((?!\n)\s){{2,}}{0}'

    # 3. wrong single whitespace: [\t\r\f\v]
    # only allow ' ' and '\n'.
    # prefix check.
    p31 = '{0}(?![ \n])\s{{1}}{1}'
    # suffix check.
    p32 = '{1}(?![ \n])\s{{1}}{0}'

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
    p1 = '{0}((?!\n)\s)+{1}'
    # suffix check.
    p2 = '{1}((?!\n)\s)+{0}'

    return list(map(
        methodcaller('format', a, b),
        [p1, p2],
    ))


@error_code
def check_e101(text_element):

    return check_on_patterns(
        single_space_patterns(ZH_CHARACTERS, '[a-zA-z]'),
        text_element,
    )


@error_code
def check_e102(text_element):

    return check_on_patterns(
        single_space_patterns(ZH_CHARACTERS, '\d'),
        text_element,
    )


@error_code
def check_e103(text_element):

    return check_on_patterns(
        single_space_patterns(
            '\d',
            # non-digit, non-chinese, ％, ℃, x, n.
            '(?!\d|{0}|{1}|[!-/:-@\[-`{{-~]|\s)[^\uff05\u2103xn\%]'.format(
                ZH_CHARACTERS, ZH_SYMBOLS,
            ),
            b_join_a=False,
        ),
        text_element,
    )


@error_code
def check_e104(text_element):

    pattern = r'([(\uff08])\d+([)\uff09])'

    def callback(text_element):
        content = text_element.content

        for m in re.finditer(pattern, content, flags=re.UNICODE):
            if m.group(1) != '(' or m.group(2) != ')':
                yield m.start(), m.end()

            i = m.start()
            if i == 0:
                continue
            i -= 1

            c = 0
            while i >= 0 and content[i] in (' ', '\n'):
                i -= 1
                c += 1

            if c != 1:
                yield i + 1, m.end()
            else:
                continue

    return check_on_callback(callback, text_element)


@error_code
def check_e203(text_element):

    return check_on_patterns(
        no_space_patterns(
            ZH_SYMBOLS,
            '(?!{0}|\s).'.format(ZH_SYMBOLS),
        ),
        text_element,
    )


@error_code
def check_e205(text_element):

    def callback(text_element):
        p = r'\.{2,}|。{2,}'
        for m in re.finditer(p, text_element.content, flags=re.UNICODE):
            detected = m.group(0)
            if detected[0] == '.' and len(detected) == 6:
                continue
            else:
                yield m.start(), m.end()

    return check_on_callback(callback, text_element)


@error_code
def check_e206(text_element):

    p1 = r'!{2,}'
    p2 = r'！{2,}'

    return check_on_patterns(
        [p1, p2],
        text_element,
    )


@error_code
def check_e207(text_element):

    p1 = r'~+'

    return check_on_patterns(
        [p1],
        text_element,
    )


@error_code
def check_e301(text_element):

    PATTERN_WORD = [
        (r'app', 'App'),
        (r'android', 'Android'),
        (r'ios', 'iOS'),
        (r'iphone', 'iPhone'),
        (r'app\s?store', 'App Store'),
        (r'wi-*fi', 'WiFi'),
        (r'e-*mail', 'email'),
        (r'P\.*S\.*', 'P.S.'),
    ]

    def callback(text_element):

        for pattern, correct_form in PATTERN_WORD:

            p1 = '(?<![a-zA-Z]){0}(?![a-zA-Z])'.format(pattern)
            p2 = '^{0}(?![a-zA-Z])'.format(pattern)
            p3 = '(?<![a-zA-Z]){0}$'.format(pattern)

            for p in [p1, p2, p3]:
                for m in re.finditer(
                    p, text_element.content,
                    flags=re.UNICODE | re.IGNORECASE,
                ):
                    if m.group(0) != correct_form:
                        yield m.start(), m.end()

    return check_on_callback(callback, text_element)


def check_block_level_error(text_element):

    BLOCK_LEVEL_CHECKING = [
        'E101',
        'E102',
        'E103',
        'E104',

        'E203',
        'E205',
        'E206',
        'E207',

        'E301',
    ]
    ret = True
    for error_code in BLOCK_LEVEL_CHECKING:
        checker = globals()['check_{0}'.format(error_code.lower())]
        _ret = checker(text_element)
        ret = ret and _ret
    return ret


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
    SENTENCE_SEPS = (
        '\.{6}'
        '|'
        '!|;|\.|\?'
        '|'
        '\uff01|\uff1b|\u3002|\uff1f'
    )
    sentences = []
    for element in elements:
        content = element.content.strip('\n')

        loc_begin = int(element.loc_begin)
        sbegin = 0

        for m in re.finditer(SENTENCE_SEPS, content, flags=re.UNICODE):
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


def detect_errors(text_element):
    _r1 = check_block_level_error(text_element)
    _r2 = True
    return _r1 and _r2
