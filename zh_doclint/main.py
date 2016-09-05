# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from os.path import expanduser

import click

from zh_doclint.metadata import VERSION
from zh_doclint.preprocessor import transform
from zh_doclint.detect_errors import detect_errors


def load_file(fpath):
    fpath = expanduser(fpath)
    with open(fpath, encoding='utf-8') as fin:
        return fin.read()


click.disable_unicode_literals_warning = True


@click.command()
@click.version_option(VERSION)
@click.argument('fpath')
def entry_point(fpath):

    ret = True
    for text_element in transform(load_file(fpath)):
        _ret = detect_errors(text_element)
        ret = ret and _ret

    return 0 if ret else 1
