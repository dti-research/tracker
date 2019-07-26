# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import click

from tracker import version
from tracker.utils import click_utils

# Import commands
from .create import create
from .run import run


@click.group(cls=click_utils.Group)
@click.version_option(
    version=version(),
    prog_name="tracker",
    message="%(prog)s %(version)s"
)

# @click.option(
#     "--debug", "log_level",
#     help="Log more information during command.",
#     flag_value=logging.DEBUG)

@click_utils.use_args

def main(args):
    """Tracker command line interface."""
    # Do noting


main.add_command(create)
main.add_command(run)
