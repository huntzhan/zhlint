# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import click
from mistune import preprocessing

from zh_doclint.metadata import VERSION
from zh_doclint.utils import load_file
from zh_doclint.preprocessor import transform

from zh_doclint.error_detection import process_errors
from zh_doclint.error_display import ErrorDisplayHandler
from zh_doclint.error_correction import (
    ErrorCorrectionHandler,
    DiffOperationExecutor,
)


click.disable_unicode_literals_warning = True


@click.command()
@click.argument('fpath', type=click.Path(exists=True))
def check(fpath):

    display_handler = ErrorDisplayHandler()

    for text_element in transform(load_file(fpath)):
        process_errors(display_handler, text_element)

    return 0 if display_handler.detected_error else 1


@click.command()
@click.argument('fpath', type=click.Path(exists=True))
def fix(fpath):
    file_content = preprocessing(load_file(fpath))
    text_elements = transform(file_content)

    correction_handler = ErrorCorrectionHandler(file_content, text_elements)
    for text_element in text_elements:
        process_errors(correction_handler, text_element)

    try:
        correction_executor = DiffOperationExecutor(
            correction_handler.diffs,
            correction_handler.raw_lines,
        )
        click.echo(correction_executor.apply_diff_operations())
        return 0
    except RuntimeError:
        click.echo('Something Wrong.')
        return 1


@click.group()
@click.version_option(VERSION)
def entry_point():
    pass


entry_point.add_command(check)
entry_point.add_command(fix)
