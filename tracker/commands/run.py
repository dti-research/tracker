# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to run an experiment
"""


import click

from tracker.utils import click_utils


@click.command("run")

@click.pass_context
@click_utils.use_args


def run(ctx, args):
    """Running a new experiment
    """
    # DEBUG
    print("run called")
