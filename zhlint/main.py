# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import cProfile
from functools import wraps

import click
from mistune import preprocessing

from zhlint.metadata import VERSION
from zhlint.utils import write_file
from zhlint.preprocessor import transform

from zhlint.error_detection import process_errors
from zhlint.error_display import ErrorDisplayHandler
from zhlint.error_correction import (
    ErrorCorrectionHandler,
    DiffOperationExecutor,
)


click.disable_unicode_literals_warning = True


def enable_debug(func):

    @click.option('--debug/--no-debug', default=False)
    @wraps(func)
    def wrapper(debug, *args, **kwargs):
        if debug:
            cProfile.runctx(
                'func(*args, **kwargs)', globals(), locals(),
                sort='cumtime',
            )
        else:
            return func(*args, **kwargs)

    return wrapper


@click.command()
@click.argument('src', type=click.File(encoding='utf-8'))
@enable_debug
def check(src):

    display_handler = ErrorDisplayHandler()

    for text_element in transform(src.read()):
        process_errors(display_handler, text_element)

    sys.exit(0 if not display_handler.detected_error else 1)


@click.command()
@click.argument('src', type=click.File(encoding='utf-8'))
@click.argument('dst', default='')
@enable_debug
def fix(src, dst):
    file_content = preprocessing(src.read())
    text_elements = transform(file_content)

    correction_handler = ErrorCorrectionHandler(file_content, text_elements)
    for text_element in text_elements:
        process_errors(correction_handler, text_element)

    try:
        correction_executor = DiffOperationExecutor(
            correction_handler.diffs,
            correction_handler.raw_lines,
        )
        fixed = correction_executor.apply_diff_operations()
    except RuntimeError:
        click.echo('Something Wrong.')
        sys.exit(1)

    if not dst:
        click.echo(fixed)
    else:
        write_file(dst, fixed)
    sys.exit(0)


@click.group()
@click.version_option(VERSION)
def entry_point():
    pass


entry_point.add_command(check)
entry_point.add_command(fix)
