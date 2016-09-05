# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re
from operator import methodcaller


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


def error_code(func):
    ERROR_TEMPLATE = (
        '{0}: {1}\n'
        '{2}\n'
    )

    code = func.__name__[-4:].upper()

    def wrapper(text_element):

        detected = func(text_element)
        if detected:
            log = ERROR_TEMPLATE.format(
                code, ERRORS[code],
                detected,
            )
            print(log)
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

    loc_detected = []
    for i, j, detected in callback(text_element):
        loc_detected.append(
            (get_loc(i, j), detected),
        )

    if not loc_detected:
        return False
    else:
        lines = []
        for loc, detected in loc_detected:
            if loc[0] == loc[1]:
                loc_text = str(loc[0])
            else:
                loc_text = '{0}-{1}'.format(*map(str, loc))

            lines.append(
                'LINE {0}\nDETECTED:{1}\nREPR:{2}'.format(
                    loc_text, detected, repr(detected),
                ),
            )
            lines.append(
                '------------------------------------------',
            )
        return '\n'.join(lines)


def check_on_patterns(patterns, text_element):

    def patterns_callback(text_element):

        for pattern in patterns:
            for m in re.finditer(pattern, text_element.content, re.UNICODE):
                yield m.start(), m.end(), m.group(0)

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
                yield m.start(), m.end(), m.group(0)

            i = m.start()
            if i == 0:
                continue
            i -= 1

            c = 0
            while i >= 0 and content[i] in (' ', '\n'):
                i -= 1
                c += 1

            if c != 1:
                yield i + 1, m.end(), content[i + 1:m.end()]
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
                yield m.start(), m.end(), detected

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
        (r'app\sstore', 'App Store'),
        (r'wi-*fi', 'WiFi'),
        (r'e-*mail', 'email'),
        (r'P\.*S\.*', 'P.S.'),
    ]

    def callback(text_element):

        for pattern, correct_form in PATTERN_WORD:
            for m in re.finditer(
                pattern, text_element.content,
                flags=re.UNICODE | re.IGNORECASE,
            ):
                if m.group(0) != correct_form:
                    yield m.start(), m.end(), m.group(0)

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


def detect_errors(text_element):
    _r1 = check_block_level_error(text_element)
    _r2 = True
    return _r1 and _r2
