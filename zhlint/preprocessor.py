# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import re

# from mistune import Markdown
from zhlint.mistune_patch import (
    HackedRenderer,
    HackedBlockGrammar, HackedBlockLexer,
    HackedInlineLexer,
    HackedMarkdown,
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

    if len(elements) >= 2:
        # fix the content and loc of the last element.
        last_content = elements[-2].content
        last_loc_end = elements[-2].loc_end

        # remove 2 additional newlines.
        last_content = last_content[:-2]
        if last_content and last_content[-1] == '\n':
            last_loc_end -= 2
        else:
            last_loc_end -= 1

        elements[-2].loc_end = last_loc_end
        elements[-2].content = last_content

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
    # doulbe \n is required for files without tailing \n.
    text += '\n\nEOF'

    hacked_md = HackedMarkdown(
        renderer=HackedRenderer(),
        inline=HackedInlineLexer,
        block=HackedBlockLexer(rules=HackedBlockGrammar()),
    )
    text = hacked_md(text)

    return generate_text_elements(text)
