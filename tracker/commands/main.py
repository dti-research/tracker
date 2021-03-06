# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import os

import click

from tracker import version
from tracker.utils import click_utils
from tracker.utils import config
from tracker.utils import log
from tracker.utils import utils

# Custom click commands
from .cd import cd
from .compare import compare
from .create import create
from .diff import diff
from .experiment import experiment
from .experiments import experiments
from .gpus import gpus
from .ls import ls
from .remote import remote
from .remotes import remotes
from .rm import rm
from .run import run
from .watch import watch

try:
    _home = os.environ["VIRTUAL_ENV"]
except KeyError:
    _home = os.path.expanduser("~")

DEFAULT_TRACKER_HOME = os.path.join(_home, ".tracker")


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
@click.option(
    "--cwd", metavar="PATH",
    help=(
        "Use PATH as current directory for referencing Tracker "
        "files (tracker.yaml)."),
    default="."
)
@click.option(
    "--tracker_home", metavar="PATH",
    help="Use PATH as Tracker home (default is {})."
         .format(DEFAULT_TRACKER_HOME),
    default=DEFAULT_TRACKER_HOME,
    envvar="TRACKER_HOME"
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

    # Configure current working directory
    config.set_cwd(utils.get_validated_dir_path(args.cwd))

    # Configure Tracker Home
    config.set_tracker_home(
        utils.get_validated_dir_path(args.tracker_home,
                                     abs=True,
                                     create=True))


main.add_command(cd)
main.add_command(compare)
main.add_command(create)
main.add_command(diff)
main.add_command(experiment)
main.add_command(experiments)
main.add_command(gpus)
main.add_command(ls)
main.add_command(remote)
main.add_command(remotes)
main.add_command(rm)
main.add_command(run)
main.add_command(watch)
