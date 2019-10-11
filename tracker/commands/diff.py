# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to get diff between two or three experiments or trials
"""

# diff -ru [FILE1] [FILE2]
# colordiff -ru [FILE1] [FILE2]
# meld [FILE1] [FILE2] [FILE3]

import logging
import os
import subprocess

import click

from tracker import run as runlib
from tracker.utils import cli
from tracker.utils import click_utils
from tracker.utils import command
from tracker.utils import config
from tracker.utils import path as pathlib

log = logging.getLogger(__name__)

DEFAULT_DIFF_CMD = "diff -ru"


def _get_all_trials():
    experiments = config.get_project_config().get("experiments")
    run_ids = []

    for exp in experiments:
        # runs_dir = pathlib.experiment_runs_dir(exp)
        runs_dir = ("/home/nily/Workspace/ml-template-ws/examples"
                    "/fashion_mnist/env/.tracker/experiments/" + exp)  # HACK!
        run_ids.extend(pathlib.get_immediate_subdirectories(runs_dir))

    return [run_id[:8] for run_id in run_ids]


def get_all_trials(ctx, args, incomplete):
    return [x for x in _get_all_trials() if incomplete in x]


def get_builtin_diff_commands(ctx, args, incomplete):
    return [x for x in ["\"diff -ru\"", "\"colordiff -ru\"", "meld"]
            if incomplete in x]


def diff_params(fn):
    click_utils.append_params(fn, [
        click.Argument(
            ("runs",),
            metavar="[RUN1 [RUN2]]",
            nargs=-1,
            autocompletion=get_all_trials),
        click.Option(
            ("-a", "--attrs"),
            is_flag=True,
            help=(
                "Diff all run attributes; if specified other "
                "attribute options are ignored.")),
        click.Option(
            ("--cmd",),
            metavar="CMD",
            help="Command used to diff runs. Supported are: diff (default),"
            "colordiff and Meld",
            autocompletion=get_builtin_diff_commands),
        click.Option(
            ("-c", "--sourcecode"),
            is_flag=True,
            help="Diff run source code."),
        click.Option(
            ("-o", "--output"),
            is_flag=True,
            help="Diff run output."),
        click.Option(
            ("-e", "--env"),
            is_flag=True,
            help="Diff run environment."),
        click.Option(
            ("-p", "--parameters"),
            is_flag=True,
            help="Diff run parameters."),
        click.Option(
            ("-r", "--resources"),
            is_flag=True,
            help="Diff run resources."),
    ])
    return fn


@click.command("diff")
@diff_params

@click.pass_context
@click_utils.use_args

def diff(ctx, args):
    """ Diff two runs.

        If `RUN1` and `RUN2` are omitted, the latest two runs are
        diffed.

        If `RUN1` or `RUN2` is specified, both must be specified.

        ### Diff Sourcecode

        Use `--soucecode` to diff sourcecode between two runs.

        ### Diff Command

        By default the ``diff`` program is used to diff run details. An
        alternative default command may be specified in
        ``~/.tracker/tracker.yaml`` using the ``command`` attribute of the
        ``diff`` key.

        To use a specific diff program with the command, use `--cmd`.
    """

    _maybe_apply_default_runs(args)
    _diff_runs(args)


def _diff_runs(args):
    assert len(args.runs) == 2, args
    assert args.runs[0] is not None and args.runs[1] is not None, args

    run1 = runlib.run_dir_for_id(args.runs[0])
    run2 = runlib.run_dir_for_id(args.runs[1])

    for path in _diff_paths(args):
        _diff(
            os.path.join(run1, path),
            os.path.join(run2, path),
            args)


def _diff(path1, path2, args):
    cmd_base = command.shlex_split(_diff_cmd(args))
    cmd = cmd_base + [path1, path2]
    log.debug("diff cmd: %r", cmd)
    try:
        subprocess.call(cmd)
    except OSError as e:
        cli.error("error running '%s': %s" % (" ".join(cmd), e))


def _diff_paths(args):
    paths = []
    if args.attrs:
        paths.append(os.path.join(".tracker", "attrs"))
        if args.env:
            log.warning("ignoring --env (already included in --attrs)")
        if args.parameters:
            log.warning("ignoring --parameters (already included in --attrs)")
        if args.resources:
            log.warning("ignoring --resources (already included in --attrs)")
    else:
        if args.env:
            paths.append(os.path.join(".tracker", "attrs", "env"))
        if args.parameters:
            paths.append(os.path.join(".tracker", "attrs", "parameters"))
        if args.resources:
            paths.append(os.path.join(".tracker", "attrs", "resources"))
    if args.output:
        paths.append(os.path.join(".tracker", "output"))
    if args.sourcecode:
        paths.append(os.path.join(".tracker", "sourcecode"))
    if not paths:
        paths.append("")
    return paths


def _maybe_apply_default_runs(args):
    n_runs = len(args.runs)
    if n_runs == 0:
        raise NotImplementedError
        # args.run = ("2", "1")
    elif n_runs == 1:
        cli.out(
            "The `diff` command requires two runs.\n"
            "Try specifying a second run or 'tracker diff --help' "
            "for more information.")
        cli.error()
    elif n_runs > 2:
        cli.out(
            "The `diff` command cannot compare more than two runs.\n"
            "Try specifying just two runs or 'tracker diff --help' "
            "for more information.")
        cli.error()
    else:
        assert n_runs == 2, args


def _diff_cmd(args):
    return args.cmd or _config_diff_cmd() or DEFAULT_DIFF_CMD


def _config_diff_cmd():
    return config.get_user_config().get("diff", {}).get("command")
