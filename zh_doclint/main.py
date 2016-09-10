# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import click

from zh_doclint.metadata import VERSION
from zh_doclint.preprocessor import transform
from zh_doclint.error_detection import process_errors
from zh_doclint.error_display import ErrorDisplayHandler
from zh_doclint.utils import load_file


click.disable_unicode_literals_warning = True


@click.command()
@click.version_option(VERSION)
@click.argument('fpath')
def entry_point(fpath):

    display_handler = ErrorDisplayHandler()

    for text_element in transform(load_file(fpath)):
        process_errors(display_handler, text_element)

    return 0 if display_handler.detected_error else 1
