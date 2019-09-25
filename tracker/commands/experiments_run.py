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
import os

import click

from tracker import deps
from tracker import operation as oplib
from tracker.utils import cli, click_utils, config

log = logging.getLogger(__name__)


def get_experiment_files(ctx, args, incomplete):
    return [k for k in glob.glob('**/*.yaml',
                                 recursive=True) if incomplete in k]


def run_params(fn):
    click_utils.append_params(fn, [
        click.Option(
            ("--run-dir",), metavar="DIR",
            help=(
                "Use alternative run directory DIR.")),
        click.Option(
            ("--gpus",), metavar="DEVICES",
            help=("Limit availabe GPUs to DEVICES, a comma separated list of "
                  "device IDs. By default all GPUs are available. Cannot be"
                  "used with --no-gpus.")),
        click.Option(
            ("--no-gpus",), is_flag=True,
            help="Disable GPUs for run. Cannot be used with --gpu."),
        click.Option(
            ("-o", "--optimizer",), metavar="ALGORITHM",
            help=(
                "Optimize the run using the specified algorithm. See "
                "Optimizing Runs for more information.")),
        click.Option(
            ("-O", "--optimize",), is_flag=True,
            help="Optimize the run using the default optimizer."),
        click.Option(
            ("--random-seed",), metavar="N", type=int,
            help=(
                "Random seed used when sampling trials or flag values. "
                "If used with --n-trials all trials will be conducted using "
                "the same seed.")),
        click.Option(
            ("-n", "--n-trials"), metavar="N", type=int,
            help="Number of trials to conduct on the given experiment."),
        click.Option(
            ("-r", "--remote"), metavar="REMOTE",
            help="Run the operation remotely.",
            autocompletion=config.get_remote_names),
        click.Option(
            ("-q", "--quiet",),
            help="Do not show output.",
            is_flag=True),
    ])
    return fn


@click.command("run")
@click.argument("experiment", type=click.STRING,
                autocompletion=get_experiment_files)
@run_params
@click_utils.no_prompt_option
@click.pass_context
@click_utils.use_args

def run(ctx, args):
    """Runs an experiment
    """
    # Sanity check
    if args.experiment not in glob.glob('**/*.yaml', recursive=True):
        cli.error("'{}' no such experiment exists"
                  .format(args.experiment))

    # Prompt user to confirm run parameters
    if args.yes or _confirm_run():
        _run(args)


def _run(args):
    # TODO: Get experiment parameters!
    # Load configuration file
    config_dict = config.load(args.experiment)
    log.debug(config_dict)

    # Create operation object
    op = oplib.Operation(
        _op_run_dir(args),
        _op_gpus)

    # Check if we should run remote or local
    if args.remote:
        _run_remote(op, args)
    else:
        _run_local(op, args)


def _run_remote(op, args):
    cli.out("Conducting experiment: {} on {}"
            .format(args.experiment, args.remote))
    raise NotImplementedError


def _run_local(op, args):
    cli.out("Conducting experiment: {}"
            .format(args.experiment))

    try:
        returncode = op.run()
    except deps.DependencyError as e:
        cli.error("Run failed as a dependency was not met: {}".format(e))
    except oplib.ProcessError as e:
        cli.error("Run failed: {}".format(e))
    else:
        if returncode != 0:
            print(returncode)
            cli.error(exit_status=returncode)


def _op_run_dir(args):
    if args.run_dir:
        run_dir = os.path.abspath(args.run_dir)
        if os.getenv("NO_WARN_RUNDIR") != "1":
            cli.out(
                "Run directory is '{}' (results will not be "
                "visible to Tracker)".format(run_dir))
        return run_dir
    else:
        return None


def _op_gpus(args):
    assert not (args.no_gpus and args.gpus)
    if args.no_gpus:
        return ""
    elif args.gpus is not None:
        return args.gpus
    return None  # use all available (default)


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
