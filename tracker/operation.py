# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from tracker import run
from tracker.utils import timestamp
from tracker.utils import path as pathlib

log = logging.getLogger(__name__)


class ProcessError(Exception):
    pass


class Operation():

    def __init__(self,
                 run_dir=None,
                 # resource_config=None,
                 # extra_attrs=None,
                 gpus=None):
        self.cmd_env = _init_cmd_env(gpus)
        self._run_dir = run_dir
        # self.resource_config = resource_config or {}
        # self.extra_attrs = extra_attrs
        self.gpus = gpus
        self._started = None
        self._stopped = None
        self._run = None
        self._proc = None
        self._exit_status = None

    def run(self):
        log.debug("tracker.Operation.run()")
        self._init_run(self._run_dir)

        # Start the process
        self._started = timestamp.timestamp()
        self._run.write_attr("started", self._started)
        try:
            self.resolve_deps()
            return self.proc()
        finally:
            print("finally")
            # self._cleanup()

    def _init_run(self, path):
        log.debug("tracker.Operation._init_run()")

        if not path:
            run_id = run.mkid()
            path = os.path.join(pathlib.runs_dir(), run_id)
        else:
            run_id = os.path.basename(path)

        self._run = run.Run(run_id, path)

        log.debug("initializing run in %s", self._run.path)

        self._run.init_skel()
        # self._init_attrs()
        # self._copy_sourcecode()
        # self._init_digests()

    def resolve_deps(self):
        assert self._run is not None
        log.debug("tracker.Operation.resolve_deps()")
        # TODO

    def proc(self):
        try:
            log.debug("tracker.Operation.proc()")
            # self._pre_proc()
        except subprocess.CalledProcessError as e:
            return e.returncode
        else:
            return self._foreground_proc()

    def _foreground_proc(self):
        log.debug("tracker.Operation._foreground_proc()")


def _init_cmd_env(gpus):
    # TODO
    env = "util.safe_osenv()"
    return env
