# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Implementation of compare
"""

# import csv
# import itertools
import logging
# import sys

from tracker.utils import cli
from tracker.utils import config

log = logging.getLogger(__name__)

BASE_COLS = ",".join([
    ".run",
    ".operation",
    ".started",
    ".time",
    ".status",
    ".label",
])

EXTRA_COLS = ".sourcecode"

MIN_COLS = ".run"

NO_RUNS_CAPTION = "no runs"

NO_TABLE_CLIP_WIDTH = pow(10, 10)


def main(args):
    _validate_args(args)
    _maybe_apply_strict_cols(args)
    if args.csv:
        _write_csv(args)
    elif args.table:
        _print_table(args)
    else:
        _tabview(args)


def _validate_args(args):
    if args.csv and args.table:
        cli.error("--table and --csv cannot both be specified")


def _maybe_apply_strict_cols(args):
    if args.strict_cols:
        if args.cols:
            cli.error("--strict-cols and --cols cannot both be specified")
        args.cols = args.strict_cols
        args.skip_core = True
        args.skip_op_cols = True


def _write_csv(args):
    # TODO
    raise NotImplementedError


def _print_table(args):
    # TODO
    raise NotImplementedError


def _tabview(args):
    config.set_log_output(True)
    # TODO
    raise NotImplementedError
