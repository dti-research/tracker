# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility class for getting measurements from NVIDIA GPUs
"""

# Copyright 2017-2019 TensorHub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division

import csv
import io
import subprocess
import sys

from tracker.utils import cli
from tracker.utils import utils


STATS = [
    "count",
    "driver_version",
    "name",
    "index",
    "pci.bus_id",
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
# For all stats run: `nvidia-smi --help-query-gpu`


class GPUPlugin():

    _stats_cmd = None

    def __init__(self):
        self._stats_cmd = _stats_cmd()

    def get_gpu_summary(self):
        if not self._stats_cmd:
            cli.error("nvidia-smi not available")
        stats = []
        for raw in self._read_raw_gpu_stats(self._stats_cmd):
            stats.append(self._format_gpu_stats(raw))
        return stats

    def _format_gpu_stats(self, raw):
        assert len(raw) == len(STATS)
        return dict(zip(STATS, [r.strip(" ") for r in raw]))

    def _read_raw_gpu_stats(self, stats_cmd):
        p = subprocess.Popen(stats_cmd, stdout=subprocess.PIPE)
        raw_lines = _read_csv_lines(p.stdout)
        result = p.wait()
        if result == 0:
            return raw_lines
        else:
            return []


def _stats_cmd():
    nvidia_smi = utils.which("nvidia-smi")
    if not nvidia_smi:
        return None
    else:
        return [
            nvidia_smi,
            "--format=csv,noheader",
            "--query-gpu=%s" % ",".join(STATS),
        ]


def _read_csv_lines(raw_in):
    csv_in = raw_in if sys.version_info[0] == 2 else io.TextIOWrapper(raw_in)
    return list(csv.reader(csv_in))


# Everything below is kept for book keeping
def _parse_raw(raw, parser):
    stripped = raw.strip()
    if stripped == "[Not Supported]":
        return None
    else:
        return parser(stripped)


def _parse_pstate(val):
    assert val.startswith("P"), val
    return int(val[1:])


def _parse_int(val):
    return int(val)


def _parse_percent(val):
    assert val.endswith(" %"), val
    return float(val[0:-2]) / 100


def _parse_bytes(val):
    assert val.endswith(" MiB"), val
    return int(val[0:-4]) * 1024 * 1024


def _parse_watts(val):
    assert val.endswith(" W"), val
    return float(val[0:-2])
