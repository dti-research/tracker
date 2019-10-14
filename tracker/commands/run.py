# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to run an experiment
"""

import logging
import os

import click

from tracker import operation as oplib
from tracker import remote as remotelib
# from tracker import resources

from tracker.utils import cli
from tracker.utils import click_utils
from tracker.utils import config
from tracker.utils import path as pathlib

log = logging.getLogger(__name__)


DEFAULT_EXE = "docker-compose up"
DEFAULT_OP = "train"


def _get_experiment_names():
    project_config = config.get_project_config()
    # TODO: Add all op names to respective experiments.
    return project_config["experiments"]


def get_experiment_names(ctx, args, incomplete):
    return [k for k in _get_experiment_names() if incomplete in k]


def run_params(fn):
    click_utils.append_params(fn, [
        click.Option(
            ("-b", "--background",), is_flag=True,
            help="Run operation in background."),
        click.Option(
            ("--gpus",), metavar="DEVICES",
            help=("Limit availabe GPUs to DEVICES, a comma separated list of "
                  "device IDs. By default all GPUs are available. Cannot be"
                  "used with --no-gpus.")),
        click.Option(
            ("--no-gpus",), is_flag=True,
            help="Disable GPUs for run. Cannot be used with --gpu."),
        click.Option(
            ("--optimizer",), metavar="ALGORITHM",
            help=(
                "Optimize the run using the specified algorithm. See "
                "Optimizing Runs for more information.")),
        # click.Option(
        #     ("--optimize",), is_flag=True,
        #     help="Optimize the run using the default optimizer."),
        # click.Option(
        #     ("-q", "--quiet",),
        #     help="Do not show output.",
        #     is_flag=True),
        click.Option(
            ("--run-dir",), metavar="DIR",
            help=(
                "Use alternative run directory DIR.")),
        click.Option(
            ("-r", "--remote",), metavar="REMOTE",
            help="Run the operation remotely.",
            autocompletion=config.get_remote_names),
        click.Option(
            ("--seed",), metavar="N", type=int,
            help=(
                "Random seed used when sampling trials or flag values. "
                "If used with --n-trials all trials will be conducted using "
                "the same seed.")),
        click.Option(
            ("--trials",), metavar="N", type=int, default=1,
            help="Number of trials to conduct on the given experiment."),
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
    # Strip potential operation from experiment name
    exp_name, op_name = _strip_op_name_from_experiment(args)
    if op_name is None:
        op_name = DEFAULT_OP
        log.debug(
            "Running experiment: '{}' with default operation: '{}' "
            "as no op was provided by the user!"
            .format(exp_name, op_name))

    # Safe load of experiment file path
    try:
        exp_conf_file = \
            config.get_project_config()["experiments"].get(exp_name)
    except KeyError:
        cli.error(
            "No experiments found. "
            "Are you sure you're in a Tracker project?")

    # Load configuration file
    exp_conf = config.load(exp_conf_file)

    # Create operation object
    op = oplib.Operation(
        op_name,
        _op_run_dir(args),
        _op_experiment(exp_name, exp_conf),
        _op_remote(args),
        _op_gpus(args))

    # Generate docker compose file

    # Prompt user to confirm run parameters
    if args.yes or _confirm_run(args, exp_name, op):
        for n in range(args.trials):
            cli.out("Trial {}/{}".format(n + 1, args.trials))
            # Run the trial
            _run(args, op)


def _run(args, op):
    cmd = ""
#    remote=None
#
#    # Generate command
#    if args.remote:
#        remote = remotelib.remote_for_args(args)
#        cmd += _remote_cmd(remote)

    cmd += DEFAULT_EXE

    log.debug("Running operation with: \"{}\"".format(cmd))

    op.run(
        cmd,
        _op_pidfile(args)
    )


def _strip_op_name_from_experiment(args):
    """ Strips name of operation from experiment name seperated with ":"

    Arguments:
        args {args} -- args from user input

    Returns:
        tuple -- Containing experiment name and operation name
    """

    value = args.experiment.split(":")
    try:
        exp_name, op_name = value
    except ValueError:
        exp_name = value[-1]
        return exp_name, None
    else:
        return exp_name, op_name


def _remote_cmd(remote):
    return "{remote_cmd} {adress} ".format(
        remote_cmd=remote.rtype,
        adress=remote.adress
    )


def _op_pidfile(args):
    if args.background:
        return pathlib.TempFile("tracker-pid-").path
    else:
        return None


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


def _op_experiment(name, experiments):
    """Get specific experiment by name

    Arguments:
        name {str} -- Name of the experiment to find in list
        experiments {list} -- List of dicts (experiments)

    Returns:
        dict -- experiment configuration
    """
    return next(x for x in experiments if name in x["experiment"])


def _op_remote(args):
    """ Get remote object

    Arguments:
        args {args} -- Arguments received from user

    Returns:
        Remote -- Instance of Remote class
    """
    if args.remote:
        return remotelib.remote_for_args(args)
    else:
        return None


def _op_gpus(args):
    assert not (args.no_gpus and args.gpus)
    if args.no_gpus:
        return ""
    elif args.gpus is not None:
        return args.gpus
    return None  # use all available (default)


""" Run confirmation prompt
"""


def _confirm_run(args, exp_name, op):
    prompt = (
        "You are about to run {trials}{exp_name}{op_name}{remote_suffix}\n"
        "{parameters}"
        "Continue?"
        .format(
            trials=_format_trials(args),
            exp_name=exp_name,
            op_name=_format_operation(op),
            remote_suffix=_format_remote_suffix(args),
            parameters=_format_parameters(op.parameters)
        ))
    return cli.confirm(prompt, default=True)


def _format_trials(args):
    if args.trials > 1:
        return "{} trials of ".format(args.trials)
    else:
        return ""


def _format_operation(op):
    return ":{}".format(op.name)


def _format_parameters(parameters):
    return "\n".join([
        "   {}: {}".format(
            p,
            parameters[p].get("value"))
        for p in sorted(parameters)
    ]) + "\n"


def _format_remote_suffix(args):
    if args.remote:
        return " on %s" % args.remote
    return ""
