# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to stop specific remote
"""

import click

from tracker import remote as remotelib
from tracker.utils import click_utils


@click.command("stop")
@remotelib.remote_arg
@click.option("-y", "--yes", is_flag=True, help="Stop without prompting.")

@click_utils.use_args

def remote_stop(args):
    remote = remotelib.remote_for_args(args)
    prompt = "WARNING: You are about to STOP %s" % remote.name
    stop_details = remote.get_stop_details()
    if stop_details:
        prompt += "\nThis will result in the following:\n"
        prompt += stop_details
    else:
        prompt += "\nThis action may result in permanent loss of data."
    remotelib.remote_op(remote.stop, prompt, False, args)
