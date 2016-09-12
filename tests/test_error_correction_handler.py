# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import os.path

from zh_doclint.error_detection import (
    process_errors,
)
from zh_doclint.preprocessor import transform
from zh_doclint.error_correction import ErrorCorrectionHandler, DiffOperation


DATA = os.path.join(
    os.path.dirname(__file__),
    'data',
)


def load_test_md(name):
    return open(os.path.join(DATA, name), encoding='utf-8').read()


def load_and_check(name):
    content = load_test_md('correction_simple.md')
    elements = transform(content)
    h = ErrorCorrectionHandler(content, elements)
    process_errors(h, elements[0])
    h.postprocess_diffs()
    return h.diffs


def test_simple():
    diffs = load_and_check('correction_simple.md')
    assert [
        DiffOperation.replace(1, 3, val='，'),
        DiffOperation.delete(1, 4),
        DiffOperation.replace(1, 7, val='。'),
    ] == diffs
