# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to create a new ML project
"""


import click

from tracker.utils import click_utils


@click.command("create")
@click.argument("name")

@click.pass_context
@click_utils.use_args


def create(ctx, args):
    """Create a new project
    """
    # DEBUG
    print("create called")
    print(args.name)
    print(ctx)
    print(args)
