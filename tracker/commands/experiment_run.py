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


def _get_experiment_names():
    project_config = config.get_project_config()
    return project_config["experiments"]


def get_experiment_names(ctx, args, incomplete):
    return [k for k in _get_experiment_names() if incomplete in k]


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
                autocompletion=get_experiment_names)
@run_params
@click_utils.no_prompt_option
@click.pass_context
@click_utils.use_args

def run(ctx, args):
    """Runs an experiment
    """
    # Safe load of experiment file path
    try:
        experiment_config_file = \
            config.get_project_config()["experiments"].get(args.experiment)
    except KeyError:
        print(
            "No experiments found. Are you sure you're in a Tracker project?")

    # Load configuration file
    experiment_config = config.load(experiment_config_file)

    # Resolve experiment operation

    # Create operation object
    #  - Here we scan through the sourcecode
    #    and extract the (hyper-)parameters
    op = oplib.Operation(
        _op_def(args),
        _op_run_dir(args),
        _get_experiment_dict_by_name(args.experiment, experiment_config),
        _op_gpus(args),
        args.yes)

    # Prompt user to confirm run parameters
    if args.yes or _confirm_run(args, op):
        _run(args, op)


def _run(args, op):
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
        print("Exited with return code {}".format(returncode))
        if returncode != 0:
            cli.error(exit_status=returncode)


def _get_experiment_dict_by_name(name, experiments):
    return next(x for x in experiments if name in x["experiment"])


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


def _op_def(args):
    # Strip op from args.

    # HACK:
    return "train"


""" Run confirmation prompt
"""


def _confirm_run(args, op):
    prompt = (
        "You are about to run {experiment}{op_def}{remote_suffix}\n"
        "{parameters}"
        "Continue?"
        .format(
            experiment=args.experiment,
            op_def=_format_operation(args),
            remote_suffix=_format_remote_suffix(args),
            parameters=_format_parameters(op.parameters)
        ))
    return cli.confirm(prompt, default=True)


def _format_operation(args):
    return ":{}".format(_op_def(args))


def _format_parameters(parameters):
    return "\n".join([
        "   {}: {}".format(
            p.get("key"),
            p.get("value"))
        for p in sorted(parameters, key=lambda k: k['key'])
    ]) + "\n"


def _format_remote_suffix(args):
    if args.remote:
        return " on %s" % args.remote
    return ""
