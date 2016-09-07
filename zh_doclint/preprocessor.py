# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re
from collections import namedtuple

from mistune import Markdown
from zh_doclint.mistune_patch import (
    HackedRenderer, HackedBlockLexer, count_newlines,
)


def remove_block(pattern, text):
    segments = []
    begin = 0

    for m in re.finditer(pattern, text, flags=re.DOTALL | re.UNICODE):
        segments.append(text[begin:m.start()])
        segments.append(b'\n' * count_newlines(m))
        begin = m.end()

    if begin < len(text):
        segments.append(text[begin:])

    return ''.join(segments)


TextElement = namedtuple(
    'TextElement',
    ['block_type', 'loc_begin', 'loc_end', 'content'],
)


def generate_text_elements(text):
    MARK_PATTERN = (
        '<<DOCLINT: TYPE=(.+?), LOC_BEGIN=(\d+), LOC_END=(\d+)>>\n'
    )

    begin = 0
    text_elements = []

    for m in re.finditer(MARK_PATTERN, text):
        if begin != m.start():
            block_type = m.group(1)
            loc_begin = m.group(2)
            loc_end = m.group(3)

            content = text[begin:m.start()]

            if content.strip():
                text_elements.append(
                    TextElement(block_type, loc_begin, loc_end, content),
                )

        begin = m.end()

    return text_elements


def transform(text):

    # latex-inline.
    text = re.sub(r'\$.+?\$', 'FORMULAR', text)
    text = re.sub(r'\\\(.+?\\\)', 'FORMULAR', text)

    # latex-block.
    text = remove_block(r'\$\$.+?\$\$', text)
    text = remove_block(r'\\\[.+?\\\]', text)

    text = remove_block(r'^\s*\-{3}.*?\-{3}', text)

    text += b'\nEOF\n'

    hacked_md = Markdown(renderer=HackedRenderer(), block=HackedBlockLexer())
    text = hacked_md(text)

    return generate_text_elements(text)
