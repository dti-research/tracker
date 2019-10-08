# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import logging
import os
import subprocess
import time

import astor

from tracker import parameters
from tracker import resources
from tracker import run
from tracker.utils import cli
from tracker.utils import command
from tracker.utils import exit_code
from tracker.utils import file as filelib
from tracker.utils import path as pathlib
from tracker.utils import timestamp
from tracker.utils import utils

log = logging.getLogger(__name__)

PROC_TERM_TIMEOUT_SECONDS = 30

DEFAULT_EXEC = "python3 -um tracker.operation_main {main}"


class ProcessError(Exception):
    pass


class Operation():

    def __init__(self,
                 op_def=None,
                 run_dir=None,
                 experiment_config=None,
                 gpus=None,
                 args_yes=False):
        self.cmd_env = _init_cmd_env(gpus)
        self._run_dir = run_dir
        self.experiment_config = experiment_config or {}
        self.resource_config = experiment_config.get("resources")
        self._op_def = op_def
        self._op_config = self._get_op_config() or {}
        self.gpus = gpus
        self.args_yes = args_yes
        self.parameters = self._init_parameters()
        self._config_parameters = None
        self._started = None
        self._stopped = None
        self._run = None
        self._proc = None
        self._exit_status = None

    @property
    def run_dir(self):
        return self._run_dir or (self._run.path if self._run else None)

    def get_name(self):
        return self._op_def

    def _get_op_config(self):
        return self.experiment_config["operations"][self._op_def]

    def run(self, background):
        self._init_run(self._run_dir)

        # Start the process
        self._started = timestamp.timestamp()
        self._run.write_attr("started", self._started)
        try:
            self.resolve_resources()
            return self.proc(background)
        finally:
            self._cleanup()

    def _init_run(self, path):
        if not path:
            experiment_runs_path = \
                pathlib.experiment_runs_dir(
                    self.experiment_config.get("experiment"))
            run_id = run.mkid()
            path = os.path.join(experiment_runs_path, run_id)
        else:
            run_id = os.path.basename(path)

        self._run = run.Run(run_id, path)

        log.debug("Initializing run in %s", self._run.path)

        self._run.init_skeleton()
        self._init_attrs()
        self._copy_sourcecode()
        # self._init_sourcecode()
        self._init_digest()

    def _init_attrs(self):
        assert self._run is not None

        self._run.write_attr("opdef", self._op_def)
        self._run.write_attr("parameters", _to_dict(self.parameters))
        # self._run.write_attr("cmd", self.cmd_args)

    def resolve_resources(self):
        assert self._run is not None
        if self._op_config.get("requires") is None:
            return

        requires = self._op_config.get("requires")
        # It doesn't matter if it has one or multiple requirements
        resolved = resources.resolve(
            requires, self.resource_config.get(requires))
        self._run.write_attr("resources", _sort_resolved(resolved))

    def proc(self, background=None):
        try:
            log.debug("tracker.Operation.proc()")
            # self._pre_proc()
        except subprocess.CalledProcessError as e:
            return e.returncode
        else:
            if background:
                self._background_proc(background)
                return 0
            return self._foreground_proc()

    def _background_proc(self, pidfile):
        import daemonize

        def action():
            return self._foreground_proc()
        daemon = daemonize.Daemonize(
            app="tracker_op", action=action, pid=pidfile)
        log.info("Operation started in background (pidfile is %s)", pidfile)
        daemon.start()

    def _foreground_proc(self):
        self._start_proc()
        self._wait_for_proc()
        self._finalize_attrs()
        return self._exit_status

    def _start_proc(self):
        assert self._proc is None
        assert self._run is not None

        log.debug("Starting operation run %s", self._run.id)

        args = split_cmd(
            DEFAULT_EXEC.format(
                main=os.path.basename(self._op_config.get("main"))
            )
        )
        env = self._proc_env()
        cwd = self._run.path

        log.debug("Starting new process with: '{}'".format(args))

        try:
            proc = subprocess.Popen(
                args,
                env=env,
                cwd=cwd,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE
            )
        except OSError as e:
            raise ProcessError(e)
        else:
            self._proc = proc
            _write_proc_lock(self._proc, self._run)

    def _wait_for_proc(self):
        assert self._proc is not None

        try:
            proc_exit_status = self._watch_proc()
        except KeyboardInterrupt:
            proc_exit_status = self._handle_proc_interrupt()
        self._exit_status = proc_exit_status
        self._stopped = timestamp.timestamp()
        _delete_proc_lock(self._run)

    def _watch_proc(self):
        assert self._proc is not None

        exit_status = self._proc.wait()
        return exit_status

    def _handle_proc_interrupt(self):
        log.info("Operation interrupted - waiting for process to exit")
        kill_after = time.time() + PROC_TERM_TIMEOUT_SECONDS
        while time.time() < kill_after:
            if self._proc.poll() is not None:
                break
            time.sleep(1)
        if self._proc.poll() is None:
            log.warning("Operation process did not exit - stopping forcefully")
            utils.kill_process_tree(self._proc.pid, force=True)
        return exit_code.SIGTERM

    def _finalize_attrs(self):
        assert self._run is not None
        assert self._exit_status is not None
        assert self._stopped is not None
        if not os.path.exists(self._run.path):
            log.warning(
                "run directory has been deleted, unable to finalize")
            return
        if not os.path.exists(self._run._tracker_dir):
            log.warning(
                "run Tracker directory has been deleted, unable to finalize")
            return
        self._run.write_attr("exit_status", self._exit_status)
        self._run.write_attr("stopped", self._stopped)

    def _proc_env(self):
        assert self._run is not None
        env = dict(self.cmd_env)
        env["RUN_DIR"] = self._run.path
        env["RUN_ID"] = self._run.id
        utils.check_env(env)
        return env

    def _copy_sourcecode(self):
        assert self._run is not None

        log.debug("Copying source code files for run {}".format(self._run.id))

        # Output dir (destination) of the sourcecode
        dest = self._run.tracker_path("sourcecode")

        # Get root of sourcecode
        root = os.path.dirname(os.path.abspath(self._op_config.get("main")))

        # Select files to copy
        rules = (
            filelib.base_sourcecode_select_rules()
        )
        select = filelib.FileSelect(root, rules)

        # Copy the files
        log.debug("Copy from: '{}' to: '{}'".format(root, dest))
        filelib.copytree(dest, select, root)

    def _init_parameters(self):
        main_entry = self._op_config.get("main")

        if main_entry:
            source = os.path.abspath(main_entry)
            if not os.path.exists(source):
                cli.error(
                    "The main entry file: '{}' does not exists!"
                    .format(source))

            # Check if user has specified parameters
            if self._op_config.get("parameters"):
                # Get all parameters from source
                source_parameters = parameters.get_parameters_from_source(
                    source)

                self._config_parameters = _create_parameter_list(
                    self._op_config.get("parameters"))

                if self._config_parameters:
                    # Check if user specified parameter values are the same
                    # as they've written in the code.
                    ast_tree = parameters.check_parameters(
                        source,
                        self._config_parameters,
                        self.args_yes)

                    # Write AST tree to source code file
                    # overwriting the original(!) # BUG
                    # TODO: Instead of overwriting the source code
                    # write the ast tree to a temp file and later
                    # copy that file into the run_dir
                    self.write_ast_to_source(ast_tree)

                # Merge the two lists and return
                # (overwriting sourcecode defaults)
                return {x["key"]: x for x in
                        source_parameters + self._config_parameters}.values()
            else:
                # Return parameters from source code
                return parameters.get_parameters_from_source(source)
        else:
            cli.error("No 'main' key is defined for operation: '{}'"
                      .format(self._op_def))

    def write_ast_to_source(self, tree):
        ast_source = astor.to_source(tree)

        main_entry = self._op_config.get("main")
        source = os.path.abspath(main_entry)

        f = open(source, "w")
        f.write(ast_source)
        f.close()

    def _cleanup(self):
        assert self._run is not None
        self._config_parameters = None
        self._started = None
        self._stopped = None
        self._run = None
        self._proc = None
        self._exit_status = None

    def _init_digest(self):
        digest = filelib.files_digest(self._run.tracker_path("sourcecode"))
        self._run.write_attr("sourcecode_digest", digest)


def _to_dict(dict_values):
    return {x["key"]: x["value"] for x in dict_values}


def _init_cmd_env(gpus):
    env = utils.safe_osenv()
    env["LOG_LEVEL"] = _log_level()
    env["CMD_DIR"] = os.getcwd()
    if gpus is not None:
        log.info(
            "Limiting available GPUs (CUDA_VISIBLE_DEVICES) to: %s",
            gpus or "<none>")
        env["CUDA_VISIBLE_DEVICES"] = gpus
    return env


def _log_level():
    try:
        return os.environ["LOG_LEVEL"]
    except KeyError:
        return str(logging.getLogger().getEffectiveLevel())


def _create_parameter_list(config_parameters):
    return [{
        "key": p,
        "value": config_parameters[p].get("value")
    } for p in config_parameters if config_parameters[p].get("value")]


def _sort_resolved(resolved):
    return {
        name: sorted(files) for name, files in resolved.items()
    }


""" Command
"""


def split_cmd(main):
    if isinstance(main, list):
        return main
    return command.shlex_split(main or "")


""" Mutex for process control
"""


def _write_proc_lock(proc, run):
    with open(run.tracker_path("LOCK"), "w") as f:
        f.write(str(proc.pid))


def _delete_proc_lock(run):
    try:
        os.remove(run.tracker_path("LOCK"))
    except OSError:
        pass
