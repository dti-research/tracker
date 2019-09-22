# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to aquire status of specific remote
"""

import click

from tracker import remote as remotelib
from tracker.utils import cli
from tracker.utils import click_utils


@click.command("status")
@remotelib.remote_arg
@click_utils.verbose_option
@click_utils.use_args

def remote_status(args):
    """ Command to aquire status of specific remote.
    """
    remote = remotelib.remote_for_args(args)
    try:
        remote.status(args.verbose)
    except remotelib.Down as e:
        cli.error(
            "Remote %s is not available (%s)" % (remote.name, e),
            exit_status=2)
    except remotelib.OperationError as e:
        cli.error(e)
