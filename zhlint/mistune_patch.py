# -*- coding: utf-8 -*-
# from __future__ import (
#     division, absolute_import, print_function, unicode_literals,
# )
# from builtins import *                  # noqa
# from future.builtins.disabled import *  # noqa

import re

from mistune import (
    Renderer,
    BlockGrammar, BlockLexer,
    InlineGrammar, InlineLexer,
    Markdown,
    _pure_pattern, _block_tag,
)
from zhlint.utils import count_newlines


class HackedRenderer(Renderer):

    def placeholder(self):
        return ''

    def block_code(self, code, lang=None):
        newlines = count_newlines(code)
        return '\n' * newlines

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
        return text

    def paragraph(self, text):
        return text

    def table(self, header, body):
        return ''

    def table_row(self, content):
        # return content
        return ''

    def table_cell(self, content, **flags):
        return ''

    def double_emphasis(self, text):
        return text

    def emphasis(self, text):
        return text

    def codespan(self, text):
        return ''

    def linebreak(self):
        return '\n'

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
        return '\n'

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


class HackedBlockGrammar(BlockGrammar):
    heading = re.compile(r'^ *(#{1,6}) *([^\n]+? *#* *(?:\n+|$))')
    lheading = re.compile(r'^([^\n]+\n) *(=|-)+ *(?:\n+|$)')

    list_item = re.compile(
        r'^('
        r'( *)(?:[*+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\2(?:[*+-]|\d+\.) )[^\n]*)*'
        # including newlines.
        r'\n*'
        r')',
        flags=re.M
    )

    fences = re.compile(
        r'^ *(`{3,}|~{3,}) *(\S+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(\n+|$)'  # ```
    )

    paragraph = re.compile(
        r'^((?:[^\n]+\n?(?!'
        r'%s|%s|%s|%s|%s|%s|%s|%s|%s'
        # including newlines.
        r'))+\n*)' % (
            _pure_pattern(fences).replace(r'\1', r'\2'),
            _pure_pattern(BlockGrammar.list_block).replace(r'\1', r'\3'),
            _pure_pattern(BlockGrammar.hrule),
            _pure_pattern(heading),
            _pure_pattern(lheading),
            _pure_pattern(BlockGrammar.block_quote),
            _pure_pattern(BlockGrammar.def_links),
            _pure_pattern(BlockGrammar.def_footnotes),
            '<' + _block_tag,
        )
    )


class HackedBlockLexer(BlockLexer):

    def __init__(self, *args, **kwargs):
        super(HackedBlockLexer, self).__init__(*args, **kwargs)
        self.loc_manager = LOCStateManager()
        self._block_level = 0

    def parse_block_quote(self, m):
        self._block_level += 1
        super(HackedBlockLexer, self).parse_block_quote(m)
        self._block_level -= 1

    def parse_fences(self, m):
        self.tokens.append({
            'type': 'code',
            'lang': m.group(2),
            'text': m.group(0),
        })

    def parse_paragraph(self, m):
        # including newlines.
        text = m.group(1)
        self.tokens.append({'type': 'paragraph', 'text': text})

    def parse_newline(self, m):
        length = len(m.group(0))
        while length > 1:
            self.tokens.append({'type': 'newline'})
            length -= 1

    def parse(self, text, rules=None):
        self.loc_manager.push()

        # including newlines.
        # text = text.rstrip('\n')

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
                if self.loc_manager.level - self._block_level == 1:
                    inject_loc_and_block_type(key, m)

                text = text[len(m.group(0)):]
                continue

            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)

        self.loc_manager.pop()
        return self.tokens


class HackedInlineGrammar(InlineGrammar):

    code = re.compile(r'^\s*(`+)\s*([\s\S]*?[^`])\s*\1(?!`)')

    text = re.compile(
        r'^[\s\S]+?'
        r'(?=[\\<!\[_*`~]|https?://| {2,}\n|$|%s)' % (
            _pure_pattern(code),
        )
    )


class HackedInlineLexer(InlineLexer):

    grammar_class = HackedInlineGrammar

    def output(self, text, rules=None):
        # including newlines.
        # text = text.rstrip('\n')

        if not rules:
            rules = list(self.default_rules)

        if self._in_footnote and 'footnote' in rules:
            rules.remove('footnote')

        output = self.renderer.placeholder()

        def manipulate(text):
            for key in rules:
                pattern = getattr(self.rules, key)
                m = pattern.match(text)
                if not m:
                    continue
                self.line_match = m
                out = getattr(self, 'output_%s' % key)(m)
                if out is not None:
                    return m, out
            return False  # pragma: no cover

        self.line_started = False
        while text:
            ret = manipulate(text)
            self.line_started = True
            if ret is not False:
                m, out = ret
                output += out
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)

        return output


class HackedMarkdown(Markdown):

    def __init__(self, *args, **kwargs):
        super(HackedMarkdown, self).__init__(*args, **kwargs)
        self._list_level = 0
        self._pre_list_level = -1
        self._token_types = set()

    def _inc_list_level(self):
        self._pre_list_level = self._list_level
        self._list_level += 1

    def _dec_list_level(self):
        self._pre_list_level = self._list_level
        self._list_level -= 1

    def _list_level_increasing(self):
        return (
            self._list_level > self._pre_list_level and
            # prefix with newline, ignore.
            self.token['type'] != 'newline'
        )

    def _record_token_types_init(self):
        self._token_types = set()

    def _only_text_and_newline_recorded(self):
        return not self._token_types - set(['text', 'newline'])

    def tok(self):
        self._token_types.add(self.token['type'])
        return super(HackedMarkdown, self).tok()

    def tok_text(self):
        self._token_types.add('text')
        return super(HackedMarkdown, self).tok_text()

    def output_list_item(self):
        self._inc_list_level()
        body = self.renderer.placeholder()

        while self.pop()['type'] != 'list_item_end':
            self._record_token_types_init()

            if self.token['type'] == 'text':
                body += self.tok_text()
            else:
                body += self.tok()

            if (
                self._list_level_increasing() and
                self._only_text_and_newline_recorded()
            ):
                body += '\n'

        self._dec_list_level()
        return self.renderer.list_item(body)

    def output_loose_item(self):
        self._inc_list_level()
        body = self.renderer.placeholder()
        while self.pop()['type'] != 'list_item_end':
            self._record_token_types_init()

            body += self.tok()

            if (
                self._list_level_increasing() and
                self._only_text_and_newline_recorded()
            ):
                body += '\n'

        self._dec_list_level()
        return self.renderer.list_item(body)

    def output(self, text, rules=None):
        self.tokens = self.block(text, rules)
        self.tokens.reverse()

        self.inline.setup(self.block.def_links, self.block.def_footnotes)

        out = self.renderer.placeholder()
        while self.pop():
            out += self.tok()
        return out
