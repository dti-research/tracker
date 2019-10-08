# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command for starting TensorBoard from within Tracker
"""

from __future__ import absolute_import
from __future__ import division

import logging

import click

from tracker import tensorboard as tb
from tracker.utils import cli
from tracker.utils import click_utils
from tracker.utils import path as pathlib
from tracker.utils import server
from tracker.utils import utils

log = logging.getLogger(__name__)


@click.command(name="tensorboard")
@server.host_and_port_options
@click.option(
    "--refresh-interval", metavar="SECONDS",
    help="Refresh interval (defaults to 5 seconds).",
    type=click.IntRange(1, None),
    default=5)
@click.option(
    "-n", "--no-open",
    help="Don't open TensorBoard in a browser.",
    is_flag=True)
@click.option("--keep-logdir", is_flag=True, hidden=True)
@click_utils.use_args

def tensorboard(args):
    """Visualize runs with TensorBoard.

    This command will start a TensorBoard process and open a browser
    window for you. TensorBoard will show the views that are selected
    using the commands filters.

    This command will not exit until you type ``Ctrl-c`` to stop it.

    TensorBoard will automatically refresh with the current run data.

    If you're prefer Tracker not open a browser window, run the
    command with the `--no-open` option.

    By default, Tracker will start the TensorBoard process on a randomly
    selected free port. If you'd like to specify the port that
    TensorBoard runs on, use the `--port` option.
    """

    tb.setup_logging()
    with pathlib.TempDir("tracker-tensorboard-", keep=args.keep_logdir) as tmp:
        logdir = tmp.path
        (log.info if args.keep_logdir else log.debug)
        ("Using logdir %s", logdir)
        monitor = tb.RunsMonitor(
            logdir,
            _list_runs_cb(args),
            args.refresh_interval)
        cli.out("Preparing runs for TensorBoard")
        monitor.run_once(exit_on_error=True)
        monitor.start()
        try:
            tb.serve_forever(
                logdir=logdir,
                host=(args.host or "0.0.0.0"),
                port=(args.port or server.free_port()),
                reload_interval=args.refresh_interval,
                ready_cb=(_open_url if not args.no_open else None))
        except tb.TensorboardError as e:
            cli.error(str(e))
        finally:
            log.debug("Stopping")
            monitor.stop()
            log.debug("Removing logdir %s", logdir)  # Handled by ctx mgr
    if utils.PLATFORM != "Windows":
        cli.out()


def _list_runs_cb(args):
    def f():
        print("hello from callback")
        # runs = runs_impl.runs_for_args(args)
        # if args.include_batch:
        #     return runs
        # return _remove_batch_runs(runs)
    return f


def _open_url(url):
    server.open_url(url)
