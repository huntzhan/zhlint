# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re

from mistune import Markdown
from zhlint.mistune_patch import (
    HackedRenderer, HackedBlockLexer, HackedInlineLexer,
    count_newlines,
)
from zhlint.utils import TextElement


def remove_block(pattern, text):
    segments = []
    begin = 0

    for m in re.finditer(pattern, text, flags=re.DOTALL | re.UNICODE):
        segments.append(text[begin:m.start()])
        segments.append('\n' * count_newlines(m))
        begin = m.end()

    if begin < len(text):
        segments.append(text[begin:])

    return ''.join(segments)


def generate_text_elements(text):
    MARK_PATTERN = (
        '<<DOCLINT: TYPE=(.+?), LOC_BEGIN=(\d+), LOC_END=(\d+)>>\n'
    )

    begin = 0
    elements = []

    for m in re.finditer(MARK_PATTERN, text):
        if begin != m.start():
            block_type = m.group(1)
            loc_begin = m.group(2)
            loc_end = m.group(3)

            content = text[begin:m.start()]

            if content.strip():
                elements.append(
                    TextElement(block_type, loc_begin, loc_end, content),
                )

        begin = m.end()

    return elements


def transform(text):

    # yaml header.
    text = remove_block(r'^\s*\-{3}.*?\-{3}', text)

    # latex-block. MUST be executed BEFORE latex-inline.
    text = remove_block(r'\$\$.+?\$\$', text)
    text = remove_block(r'\\\[.+?\\\]', text)

    # latex-inline.
    text = re.sub(r'\$.+?\$', '$$', text)
    text = re.sub(r'\\\(.+?\\\)', '\\\\\(\\\\\)', text)

    # manually add EOF.
    text += '\nEOF\n'

    hacked_md = Markdown(
        renderer=HackedRenderer(),
        inline=HackedInlineLexer,
        block=HackedBlockLexer,
    )
    text = hacked_md(text)

    return generate_text_elements(text)
