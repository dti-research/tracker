# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import click

from tracker import version
from tracker.utils import click_utils
from tracker.utils import log

# Custom click commands
from .cd import cd
from .create import create
from .experiments import experiments
from .ls import ls


@click.group(cls=click_utils.Group)
@click.version_option(
    version=version(),
    prog_name="tracker",
    message="%(prog)s %(version)s"
)

@click.option(
    '--verbose',
    is_flag=True, help='Print debug information', default=False
)

@click.option(
    u'--logfile', type=click.Path(), default=None,
    help=u'File to be used as a stream for DEBUG logging',
)

# @click.option(
#     "--debug", "log_level",
#     help="Log more information during command.",
#     flag_value=logging.DEBUG)

@click_utils.use_args

def main(args):
    """Tracker command line interface."""

    # Configure logger
    log.configure_logger(
        stream_level='DEBUG' if args.verbose else 'INFO',
        log_file=args.logfile,
    )


main.add_command(cd)
main.add_command(create)
main.add_command(experiments)
main.add_command(ls)
