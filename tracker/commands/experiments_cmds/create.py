# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to create a new ML experiment within a Tracker project
"""

import logging
import click

from tracker.utils import click_utils


log = logging.getLogger(__name__)


@click.command("create")

@click.pass_context
@click_utils.use_args

def create(ctx, args):
    """Creates a new experiment.
    """

    log.info("Experiment create called")
