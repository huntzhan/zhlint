# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from zh_doclint.utils import TextElement
from zh_doclint.error_detection import (
    process_errors,
)
from zh_doclint.error_display import ErrorDisplayHandler


def test_process_errors():

    display_handler = ErrorDisplayHandler()
    te = TextElement(
        '', '1', '2',
        '好的句子，好的句子',
    )
    process_errors(display_handler, te)
    assert not display_handler.detected_error

    display_handler = ErrorDisplayHandler()
    te = TextElement(
        '', '1', '2',
        'app坏的句子， 坏的句子',
    )
    process_errors(display_handler, te)
    assert display_handler.detected_error
