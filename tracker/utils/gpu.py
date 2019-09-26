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
        stats = []
        for raw in self._read_raw_gpu_stats(self._stats_cmd):
            stats.append(self._format_gpu_stats(raw))
        return stats

    def _format_gpu_stats(self, raw):
        return {
            "count": raw[0],
            "driver_version": raw[1],
            "name": raw[2],
            "index": raw[3],
            "pci.bus_id": raw[4],
            "fan.speed": raw[5],
            "memory.total": raw[6],
            "memory.used": raw[7],
            "memory.free": raw[8],
            "utilization.memory": raw[9],
            "utilization.gpu": raw[10],
            "compute_mode": raw[11],
            "temperature.gpu": raw[12],
            "power.draw": raw[13],
            "clocks.max.sm": raw[14],
        }

    def enabled_for_op(self, _op):
        if not self._stats_cmd:
            return False, "nvidia-smi not available"
        return True, ""

    def read_summary_values(self):
        return self._gpu_stats(self._stats_cmd) if self._stats_cmd else {}

    def _gpu_stats(self, stats_cmd):
        stats = {}
        for raw in self._read_raw_gpu_stats(stats_cmd):
            stats.update(self._calc_gpu_stats(raw))
        return stats

    def _read_raw_gpu_stats(self, stats_cmd):
        p = subprocess.Popen(stats_cmd, stdout=subprocess.PIPE)
        raw_lines = _read_csv_lines(p.stdout)
        result = p.wait()
        if result == 0:
            return raw_lines
        else:
            # self.log.debug("reading GPU stats (smi output: '%s')", raw_lines)
            return []

    @staticmethod
    def _calc_gpu_stats(raw):
        # See STATS for list of stat names/indexes
        index = raw[0]
        mem_total = _parse_raw(raw[3], _parse_bytes)
        mem_used = _parse_raw(raw[4], _parse_bytes)
        vals = [
            ("fanspeed", _parse_raw(raw[1], _parse_percent)),
            ("pstate", _parse_raw(raw[2], _parse_pstate)),
            ("mem_total", mem_total),
            ("mem_used", mem_used),
            ("mem_free", mem_total - mem_used),
            ("mem_util", _parse_raw(raw[6], _parse_percent)),
            ("util", _parse_raw(raw[5], _parse_percent)),
            ("temp", _parse_raw(raw[7], _parse_int)),
            ("powerdraw", _parse_raw(raw[8], _parse_watts))
        ]
        return dict([(_gpu_val_key(index, name), val) for name, val in vals])


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


def _gpu_val_key(index, name):
    return "sys/gpu%s/%s" % (index, name)
