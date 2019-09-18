# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to run an experiment
"""

import glob
import logging

import click

from tracker.utils import cli, click_utils, conf

log = logging.getLogger(__name__)


def get_experiments(ctx, args, incomplete):
    return [k for k in glob.glob('**/*.yaml',
                                 recursive=True) if incomplete in k]


@click.command("run")
@click.argument("experiment", type=click.STRING,
                autocompletion=get_experiments)


@click.pass_context
@click_utils.use_args


def run(ctx, args):
    """Runs an experiment
    """
    if args.experiment not in glob.glob('**/*.yaml', recursive=True):
        cli.error("'{}' no such experiment exists"
                  .format(args.experiment))

    # TODO: Get experiment parameters!
    # Load configuration file
    config_dict = conf.load(args.experiment)
    print(config_dict)

    # Prompt user to confirm run parameters
    if _confirm_run():
        cli.out("Running experiment: {}".format(args.experiment))
    else:
        cli.out("Terminated")


def _confirm_run():
    # prompt = (
    #     "You are about to {action} {op_desc}{batch_suffix}{remote_suffix}\n"
    #     "{flags}"
    #     "{resources}"
    #     "Continue?"
    #     .format(
    #         action=_action_desc(args),
    #         op_desc=_op_desc(op),
    #         batch_suffix=_batch_suffix(op, args),
    #         remote_suffix=_remote_suffix(args),
    #         flags=_format_op_flags(op),
    #         resources=_format_op_resources(op.resource_config)))
    prompt = (
        "You are about to run XXX. "
        "Continue?")
    return cli.confirm(prompt, default=True)
