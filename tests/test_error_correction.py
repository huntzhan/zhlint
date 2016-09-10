# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from zh_doclint.error_correction import ErrorCorrectionHandler
from zh_doclint.error_detection import TextElement


def test_generate_lcs_matrix():
    content = (
        'abc\n'
        '\n'
        'abc'
    )
    elements = (
        TextElement('paragraph', '1', '1', 'ac\n'),
        TextElement('paragraph', '3', '3', 'ac'),
        'EOF',
    )

    h = ErrorCorrectionHandler(content, elements)

    l1 = [True] * len(h.raw_lines[1])
    l1[1] = False
    assert l1 == h.lcs_matrix[1]

    l3 = [True] * len(h.raw_lines[3])
    l3[1] = False
    assert l3 == h.lcs_matrix[3]

    l1 = [0, 2, 3]
    assert l1 == h.index_matrix[1]

    l3 = [0, 2]
    assert l3 == h.index_matrix[3]
