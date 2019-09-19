# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to start specific remote
"""

import click

from tracker import remote as remotelib
from tracker.utils import click_utils


@click.command("start")
@remotelib.remote_arg
@click.option("-y", "--yes", is_flag=True, help="Start without prompting.")

@click_utils.use_args

def remote_start(args):
    """Start a remote.

    {{ remotelib.remote_arg }}
    """

    remote = remotelib.remote_for_args(args)
    prompt = "You are about to start %s" % remote.name
    remotelib.remote_op(remote.start, prompt, True, args)
