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
from tracker.utils import file as filelib

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
        # log.debug("tracker.Operation.run()")
        self._init_run(self._run_dir)

        # Start the process
        self._started = timestamp.timestamp()
        self._run.write_attr("started", self._started)
        try:
            self.resolve_deps()
            return self.proc()
        finally:
            log.debug("finally")
            # self._cleanup()

    def _init_run(self, path):
        if not path:
            run_id = run.mkid()
            path = os.path.join(pathlib.runs_dir(), run_id)
        else:
            run_id = os.path.basename(path)

        self._run = run.Run(run_id, path)

        log.debug("Initializing run in %s", self._run.path)

        self._run.init_skel()
        # self._init_attrs()
        self._copy_sourcecode()
        # self._init_digests()

    def resolve_deps(self):
        assert self._run is not None
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

        # DEBUG: Now everything is fine :-)
        return 0
        # return self._exit_status

    def _copy_sourcecode(self):
        assert self._run is not None

        log.debug("Copying source code files for run {}".format(self._run.id))

        # Select files to copy
        dest = self._run.tracker_path("sourcecode")

        # TODO: Get root of source code from somewhere else!
        root = '/home/nily/Workspace/ml-template-ws/testing_templates/gtsrb'

        rules = (
            filelib.base_sourcecode_select_rules()
        )
        select = filelib.FileSelect(root, rules)

        # Copy the files
        log.debug("Copy from: '{}' to: '{}'".format(root, dest))
        filelib.copytree(dest, select, root)


def _init_cmd_env(gpus):
    # TODO
    env = "util.safe_osenv()"
    return env
