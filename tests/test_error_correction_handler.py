# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import os.path

from zhlint.error_detection import (
    process_errors,
)
from zhlint.preprocessor import transform
from zhlint.error_correction import (
    ErrorCorrectionHandler,
    DiffOperation,
    DiffOperationExecutor,
)


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
    executor = DiffOperationExecutor(h.diffs, h.raw_lines)
    return executor


def test_simple():
    executor = load_and_check('correction_simple.md')
    assert [
        DiffOperation.replace(1, 3, val='，'),
        DiffOperation.delete(1, 4),
        DiffOperation.replace(1, 7, val='。'),
    ] == executor.diffs

    assert '中文，标点。\n' == executor.apply_diff_operations()
