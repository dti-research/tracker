# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to watch background processes
"""

import logging
import os
import sys
import time

import click
import psutil

from tracker import run as runlib
from tracker.utils import cli
from tracker.utils import click_utils
from tracker.utils import path as pathlib
from tracker.utils import utils

log = logging.getLogger(__name__)


@click.command("watch")

@click.option(
    "-p", "--pid", metavar="PID",
    help=("Watch the run associated with the specified process. "
          "PID may be a process ID or a path to a file containing "
          "a process ID."))
@click.pass_context
@click_utils.use_args


def watch(ctx, args):
    """Watch run output.

    By default, the command will watch output from the current running
    operation.

    ### Watch Run by PID:

    You may alternatively specify the process ID of the run to watch,
    using `--pid`. ``PID`` may be a process ID or a path to a file
    containing a process ID.
    """

    if not args.pid:
        raise NotImplementedError(
            "We currently have no idea how to determine which "
            "is the current running operation. Please provide a PID while "
            "we figure things out!")

    run = _run_for_pid_arg(args.pid)
    _watch_run(run)


def _run_for_pid_arg(pid):
    return utils.find_apply([
        _run_for_pidfile,
        _run_for_pid,
        _handle_no_run_for_pid_arg
    ], pid)


def _run_for_pidfile(pid_arg):
    pid = _read_pid(pid_arg)
    if pid is None:
        return None
    return _run_for_pid(pid)


def _read_pid(path):
    try:
        f = open(path, "r")
    except IOError as e:
        if e.errno != 2:
            raise
        return None
    else:
        raw = f.readline().strip()
        try:
            return int(raw)
        except ValueError:
            cli.error("pidfile %s does not contain a valid pid" % path)


def _run_for_pid(pid):
    pid = _try_int(pid)
    if pid is None:
        return None

    for exp in os.listdir(pathlib.path("experiments")):
        experiment_dir = os.path.join(pathlib.path("experiments"), exp)
        for run_id, run_dir in pathlib.iter_dirs(experiment_dir):
            run = runlib.Run(run_id, run_dir)
            if run.pid and (run.pid == pid or _parent_pid(run.pid) == pid):
                return run
    cli.error("cannot find run for pid %i" % pid)
    # See list of processes: $ ps -aef --forest


def _try_int(pid):
    try:
        return int(pid)
    except ValueError:
        return None


def _parent_pid(pid):
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None
    else:
        return p.parent().pid


def _watch_run(run):
    try:
        _tail(run)
        _print_run_status(run)
    except KeyboardInterrupt:
        _stopped_msg(run)


def _stopped_msg(run):
    msg = "\nStopped watching %s" % run.short_id
    if run.pid and psutil.Process(run.pid).is_running():
        msg += " (%s still running)" % run.pid
    cli.out(msg)


def _tail(run):
    if os.getenv("NO_WATCHING_MSG") != "1":
        cli.out("Watching run %s (pid: %s)" % (run.id, run.pid), err=True)
    if run.pid is None:
        _print_output(run)
        return
    proc = psutil.Process(run.pid)
    output_path = run.tracker_path("output")
    f = None
    while proc.is_running():
        f = f or _try_open(output_path)
        if not f:
            time.sleep(1.0)
            continue
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue
        sys.stdout.write(line)
        sys.stdout.flush()


def _print_output(run):
    output_path = run.tracker_path("output")
    f = _try_open(output_path)
    if not f:
        return
    while True:
        line = f.readline()
        if not line:
            break
        sys.stdout.write(line)
        sys.stdout.flush()


def _try_open(path):
    try:
        return open(path, "r")
    except OSError as e:
        if e.errno != 2:
            raise
        return None


def _print_run_status(run):
    cli.out(
        "Run %s stopped with a status of '%s'"
        % (run.short_id, run.status), err=True)


def _handle_no_run_for_pid_arg(pid_arg):
    # Assume pid_arg is a pidfile path.
    cli.error("%s does not exist" % pid_arg)
