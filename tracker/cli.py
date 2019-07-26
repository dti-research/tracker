# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

"""Main `tracker` CLI."""

import os
import sys
import click

from tracker import __version__
from tracker.main import tracker


def version_msg():
    """Return the Tracker version, location and Python powering it."""
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    message = u'Tracker v.%(version)s from {} (Python {})'
    return message.format(location, python_version)


@click.command()
@click.version_option(__version__, u'-v', u'--version', message=version_msg())
@click.argument(u'test')
def main(test):
    tracker(test)


if __name__ == "__main__":
    main()
