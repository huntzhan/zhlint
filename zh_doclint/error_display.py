# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re
import itertools
import collections as abc

import click


ERROR_DISPLAY = {
    # space.
    'E101': '英文与非标点的中文之间需要有一个空格',
    'E102': '数字与非标点的中文之间需要有一个空格',
    'E103': '除了「％」、「℃」、以及倍数单位（如 2x、3n）之外，'
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


def get_loc(element, i, j):
    begin = int(element.loc_begin)
    begin += len(list(filter(
        lambda c: c == '\n', element.content[:i],
    )))
    end = begin + len(list(filter(
        lambda c: c == '\n', element.content[i:j],
    )))
    return begin, end


def generate_detected_text(element, i, j):

    def inc(char, count):
        if 0 <= ord(char) <= 127:
            # for ASCII, increase by 1.
            return count + 1
        else:
            # otherwise, increase by 2.
            return count + 2

    OFFSET = 20
    content = element.content

    # expand to left.
    ri = i
    c = 0
    while ri >= 0 and c < OFFSET and content[ri] != '\n':
        ri -= 1
        c = inc(content[ri], c)
    ri = min(ri + 1, i)

    # expand to right.
    rj = j
    c = 0
    while rj < len(content) and c < OFFSET and content[ri] != '\n':
        rj += 1
        c = inc(content[ri], c)
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


class ErrorDisplayHandler(object):

    def __init__(self):
        self.detected_error = False

    def header_styles(self, code):
        return [
            split_bar('=', 2, code, ERROR_DISPLAY[code]),
            click.style('\n'),
            click.style(code, fg='green', bold=True),
            click.style(': '),
            click.style(ERROR_DISPLAY[code]),
            click.style('\n'),
            split_bar('=', 2, code, ERROR_DISPLAY[code]),
            click.style('\n'),
        ]

    def body_styles(self, element, matches):

        loc_detected = []
        for m in matches:
            # support context.
            if isinstance(m, abc.Sized) and len(m) == 2:
                m = m[0]

            loc_detected.append(
                (m.start(), m.end()),
            )

        styles = []
        for i, j in sorted(loc_detected):
            loc = get_loc(element, i, j)
            text_line, mark_line = generate_detected_text(element, i, j)

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

    def __call__(self, error_code, element, matches):
        if not matches:
            return
        matches = list(matches)

        if not matches:
            return
        else:
            self.detected_error = True

        for style in itertools.chain(
            self.header_styles(error_code),
            self.body_styles(element, matches)
        ):
            click.echo(style, nl=False)
        click.echo('\n', nl=False)
