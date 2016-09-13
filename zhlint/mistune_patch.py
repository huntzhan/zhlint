# -*- coding: utf-8 -*-
# from __future__ import (
#     division, absolute_import, print_function, unicode_literals,
# )
# from builtins import *                  # noqa
# from future.builtins.disabled import *  # noqa


from mistune import Renderer, BlockLexer
from zhlint.utils import count_newlines


def fmt(text):
    return '%s\n' % text.rstrip('\n')


class HackedRenderer(Renderer):

    def placeholder(self):
        return ''

    def block_code(self, code, lang=None):
        return ''

    def block_quote(self, text):
        return text

    def block_html(self, html):
        return ''

    def header(self, text, level, raw=None):
        return text

    def hrule(self):
        return ''

    def list(self, body, ordered=True):
        return body

    def list_item(self, text):
        return fmt(text)

    def paragraph(self, text):
        return fmt(text)

    def table(self, header, body):
        # return (
        #     '%s'
        #     '%s'
        # ) % (header, body)
        return ''

    def table_row(self, content):
        # return content
        return ''

    def table_cell(self, content, **flags):
        # return fmt(content)
        return ''

    def double_emphasis(self, text):
        return text

    def emphasis(self, text):
        return text

    def codespan(self, text):
        return ''

    def linebreak(self):
        return ''

    def strikethrough(self, text):
        return text

    def text(self, text):
        return text

    def escape(self, text):
        return text

    def autolink(self, link, is_email=False):
        return link

    def link(self, link, title, text):
        return text

    def image(self, src, title, text):
        return ''

    def inline_html(self, html):
        return ''

    def newline(self):
        return ''

    def footnote_ref(self, key, index):
        return ''

    def footnote_item(self, key, text):
        return ''

    def footnotes(self, text):
        return ''


class LOCStateManager(object):

    def __init__(self):
        self.loc = 1
        self.loc_stack = []

    def push(self):
        self.loc_stack.append(self.loc)

    def pop(self):
        self.loc = self.loc_stack.pop()

    @property
    def level(self):
        return len(self.loc_stack)


class HackedBlockLexer(BlockLexer):

    def __init__(self, *args, **kwargs):
        super(HackedBlockLexer, self).__init__(*args, **kwargs)
        self.loc_manager = LOCStateManager()

    def parse(self, text, rules=None):
        self.loc_manager.push()

        text = text.rstrip('\n')

        if not rules:
            rules = self.default_rules

        def manipulate(text):
            for key in rules:
                rule = getattr(self.rules, key)
                m = rule.match(text)
                if not m:
                    continue
                getattr(self, 'parse_%s' % key)(m)
                return key, m
            return False, False  # pragma: no cover

        def inject_loc_and_block_type(key, m):
            newlines = count_newlines(m)

            loc_begin = self.loc_manager.loc
            self.loc_manager.loc += newlines
            loc_end = self.loc_manager.loc

            content = m.group(0)
            i = 0
            n = len(content)
            while i < n and content[i] == '\n':
                i += 1
                loc_begin += 1
            i = n - 1
            while i >= 0 and content[i] == '\n':
                i -= 1
                loc_end -= 1

            template = '<<DOCLINT: TYPE={0}, LOC_BEGIN={1}, LOC_END={2}>>\n'
            line = template.format(
                key, str(loc_begin), str(loc_end),
            )
            self.tokens.append({
                'type': 'paragraph',
                'text': line,
            })

        while text:
            key, m = manipulate(text)
            if m is not False:
                text = text[len(m.group(0)):]

                if self.loc_manager.level == 1 or key == 'paragraph':
                    inject_loc_and_block_type(key, m)

                continue

            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)

        self.loc_manager.pop()
        return self.tokens
