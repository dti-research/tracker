# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to run an experiment
"""

import logging
import click

from tracker.utils import click_utils


log = logging.getLogger(__name__)


def get_dummy_list_of_experiments():
    return ["test", "senseact", "lol1", "final", "finalfinal"]


def get_experiments(ctx, args, incomplete):
    return [k for k in get_dummy_list_of_experiments() if incomplete in k]


@click.command("run")
@click.argument("experiment", type=click.STRING,
                autocompletion=get_experiments)


@click.pass_context
@click_utils.use_args


def run(ctx, args):
    """Running a new experiment
    """
    if args.experiment not in get_dummy_list_of_experiments():
        log.error("Error! '{}' no such experiment exists"
                  .format(args.experiment))
        exit(1)

    log.info("Running experiment: {}".format(args.experiment))
