# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to list CUDA devices available
"""

import logging

import click

from tracker import remote as remotelib
from tracker.utils import click_utils
from tracker.utils import cli
from tracker.utils import config
from tracker.utils import gpu


log = logging.getLogger(__name__)


def gpus_params(fn):
    click_utils.append_params(fn, [
        click.Option(
            ("-r", "--remote"), metavar="REMOTE",
            help="Get list of GPUs from remote.",
            autocompletion=config.get_remote_names),
    ])
    return fn


@click.command("list")
@click_utils.use_args
@gpus_params
@click.pass_context
def list_gpus(ctx, args):
    """ Lists CUDA Devices
    """
    if args.remote:
        remote = remotelib.remote_for_args(args)
        gpu_handler = gpu.GPU(remote=remote)
    else:
        gpu_handler = gpu.GPU()

    gpu_stats = gpu_handler.get_gpu_summary()

    cols = [
        "pci.bus_id",
        "index",
        "name",
        "driver_version",
        "fan.speed",
        "memory.total",
        "memory.used",
        "memory.free",
        "utilization.memory",
        "utilization.gpu",
        "compute_mode",
        "temperature.gpu",
        "power.draw",
        "clocks.max.sm",
    ]

    heading = {
        col_name: col_name
        for col_name in cols for g in gpu_stats
        if "[Not Supported]" not in g[col_name]
    }

    data = [heading] + gpu_stats

    cli.table(data,
              [c for c in cols for g in gpu_stats
               if "[Not Supported]" not in g[c]])
