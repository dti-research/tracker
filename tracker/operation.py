# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import logging
import os
import subprocess
# import sys
import time

# import astor

# from tracker import parameters
# from tracker import resources
from tracker import run
# from tracker.utils import cli
from tracker.utils import command
from tracker.utils import exit_code
from tracker.utils import file as filelib
from tracker.utils import path as pathlib
# from tracker.utils import python
from tracker.utils import timestamp
from tracker.utils import utils

log = logging.getLogger(__name__)

PROC_TERM_TIMEOUT_SECONDS = 30

# DEFAULT_EXEC = "{python} -um tracker.operation_main {main}"


class ProcessError(Exception):
    pass


class Operation():

    __properties__ = [
        "name",
        "run_dir",
        "short_id",
        "pid",
        "status",
        "timestamp",
    ]

    def __init__(self,
                 name=None,
                 run_dir=None,
                 exp_conf=None,
                 remote=None,
                 gpus=None):
        self.name = name
        self._run_dir = run_dir
        self.experiment_config = exp_conf or {}
        self.operation_config = self._get_operation_config()
        self.environments = self._get_environtment_config()
        self.parameters = self._get_parameter_config()
        self.remote = remote or None
        self.cmd = None
        self.run_cmd = None
        self._gpus = gpus
        self._started = None
        self._stopped = None
        self._run = None
        self._proc = None
        self._exit_status = None

    @property
    def run_dir(self):
        return self._run_dir or (self._run.path if self._run else None)

    def _get_operation_config(self):
        return self.experiment_config.get("operations").get(self.name)

    def _get_environtment_config(self):
        return self.operation_config.get("environments")

    def _get_parameter_config(self):
        return self.operation_config.get("parameters")

    def run(self, cmd, background):
        assert self.cmd is None
        self._init_cmd(cmd)
        self._init_run(self._run_dir)

        try:
            return self.proc(background)
        finally:
            self._cleanup()

    def _init_cmd(self, cmd):
        if self.remote:
            self.cmd = \
                "{remote_cmd} {adress} {cmd}".format(
                    remote_cmd=self.remote.rtype,
                    adress=self.remote.adress,
                    cmd=cmd
                )
        else:
            self.cmd = cmd

    def _init_run(self, run_dir):
        if not run_dir:
            exp_name = self.experiment_config.get("experiment")
            experiment_runs_path = pathlib.experiment_runs_dir(exp_name)
            run_id = run.mkid()
            run_dir = os.path.join(experiment_runs_path, run_id)
        else:
            run_id = os.path.basename(run_dir)

        self._run = run.Run(run_id, run_dir)

        log.debug("Initializing run in %s", self._run.path)

        self._run.init_skeleton()
        self._init_attrs()
        self._copy_sourcecode()
        self._init_environments()
        self._init_digest()

    def _init_attrs(self):
        assert self._run is not None

        self._run.write_attr("opdef", self.name)
        self._run.write_attr("parameters", self.parameters)
        self._run.write_attr("cmd", self.cmd)

    def _init_environments(self):
        """ Workflow:
             - Generate command to be run within the container
             - Check if gpus are requested by user
             - Create docker-compose.yaml file locally in run_dir
             - If remote, push docker-compose file to remote
             - If mount volume, copy that folder to run_dir
        """

        # Check if user requested the use of GPUs
        if self._gpus:
            assert "run" in self.cmd
            self.cmd += " " + self._container_args() \
                + " " + self.environments[0].get("image") \
                + " " + self._run_command()
        else:
            # Generate docker-compose file

            # for env in self.environments:
            print(self.cmd)
            print(self.environments)

            # Copy file to remote
            if self.remote:
                src = './docker-compose.yaml'  # HACK
                host = '/home/dti/'
                self.remote.copy_src_to_host(src, host)
            else:
                # Delete the following when generation of docker file is ready.
                #   -> Currently just a HACK to see if its running
                dest = self._run.path
                src = './docker-compose.yaml'
                import shutil
                shutil.copyfile(src, os.path.join(dest, "docker-compose.yaml"))

    def _container_args(self):
        return "{gpu_arg} {volume_arg}".format(
            gpu_arg="--gpus {}".format(self._gpus) if self._gpus else "",
            # HACK: Works only on local
            # -> Replace os.getcwd() with run-dir
            volume_arg="-v {}:/code -w /code".format(os.getcwd()),
        )

    def _run_command(self):
        return "{exec} {args}".format(
            exec=self._run_executable(),
            args=self._run_parameters()
        )

    def _run_executable(self):
        exe = self.operation_config.get("executable")
        if self.remote:
            exe = escape_quotes(exe)
        return exe

    def _run_parameters(self):
        if self.parameters:
            return " ".join([
                "--{arg_name} {arg_value}".format(
                    arg_name=p,
                    arg_value=self.parameters[p].get("value"))
                for p in sorted(self.parameters)
            ])
        else:
            return ""

    def _init_digest(self):
        digest = filelib.files_digest(self._run.tracker_path("sourcecode"))
        self._run.write_attr("sourcecode_digest", digest)

#     def resolve_resources(self):
#         assert self._run is not None
#         if self._op_config.get("requires") is None:
#             return
#
#         requires = self._op_config.get("requires")
#         # It doesn't matter if it has one or multiple requirements
#         resolved = resources.resolve(
#             requires, self.resource_config.get(requires))
#         self._run.write_attr("resources", _sort_resolved(resolved))
#
    def proc(self, background=None):
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

        args = split_cmd(self.cmd)
        # env = self._proc_env()
        cwd = self._run.path

        log.debug("Starting new process with: '{}'".format(args))
        self._run.write_attr("cmd", self.cmd, raw=True)

        try:
            proc = subprocess.Popen(
                args,
                # env=env,
                cwd=cwd,
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

    def _cleanup(self):
        assert self._run is not None
        self.cmd = None
        self._config_parameters = None
        self._started = None
        self._stopped = None
        self._run = None
        self._proc = None
        self._exit_status = None
#
#     def _proc_env(self):
#         assert self._run is not None
#         env = dict(self.cmd_env)
#         env["RUN_DIR"] = self._run.path
#         env["RUN_ID"] = self._run.id
#         utils.check_env(env)
#         return env
#

    def _copy_sourcecode(self):
        assert self._run is not None

        exe = self.operation_config.get("executable")

        log.debug(
            "Verifying that file mode bits for the executable '{}' is set"
            .format(exe))
        filelib.chmod_plus_x(exe)  # -rwxr-xr-x

        log.debug(
            "Copying source code files for run {}".format(self._run.id))

        # Output dir (destination) of the sourcecode
        dest = self._run.tracker_path("sourcecode")

        # Get root of sourcecode
        root = os.path.dirname(os.path.abspath(exe))

        # Select files to copy
        rules = (
            filelib.base_sourcecode_select_rules()
        )
        select = filelib.FileSelect(root, rules)

        # Copy the files
        log.debug("Copy from: '{}' to: '{}'".format(root, dest))
        filelib.copytree(dest, select, root)
#
#     def _init_parameters(self):
#         return self._op_config.get("parameters")
#         #main_entry = self._op_config.get("main")
# #
#         #if main_entry:
#         #    source = os.path.abspath(main_entry)
#         #    if not os.path.exists(source):
#         #        cli.error(
#         #            "The main entry file: '{}' does not exists!"
#         #            .format(source))
# #
#         #    # Check if user has specified parameters
#         #    if self._op_config.get("parameters"):
#         #        # Get all parameters from source
#         #        source_parameters = parameters.get_parameters_from_source(
#         #            source)
# #
#         #        self._config_parameters = _create_parameter_list(
#         #            self._op_config.get("parameters"))
# #
#         #        if self._config_parameters:
#         #            # Check if user specified parameter values are the same
#         #            # as they've written in the code.
#         #            ast_tree = parameters.check_parameters(
#         #                source,
#         #                self._config_parameters,
#         #                self.args_yes)
# #
#         #            # Write AST tree to source code file
#         #            # overwriting the original(!) # BUG
#         #            # TODO: Instead of overwriting the source code
#         #            # write the ast tree to a temp file and later
#         #            # copy that file into the run_dir
#         #            self.write_ast_to_source(ast_tree)
# #
#         #        # Merge the two lists and return
#         #        # (overwriting sourcecode defaults)
#         #        return {x["key"]: x for x in
#         #                source_parameters + self._config_parameters}
#                          .values()
#         #    else:
#         #        # Return parameters from source code
#         #        return parameters.get_parameters_from_source(source)
#         #else:
#         #    cli.error("No 'main' key is defined for operation: '{}'"
#         #              .format(self._op_name))
#
#     def write_ast_to_source(self, tree):
#         ast_source = astor.to_source(tree)
#
#         main_entry = self._op_config.get("main")
#         source = os.path.abspath(main_entry)
#
#         f = open(source, "w")
#         f.write(ast_source)
#         f.close()
#

#     def run(self, background):
#         self._init_run(self._run_dir)
#
#         # Check if we should initialise environment
#         # if self._env_config:
#         #    self._init_env()
#
#         # Start the process
#         self._started = timestamp.timestamp()
#         self._run.write_attr("started", self._started)
#         try:
#            self.resolve_resources()
#            return self.proc(background)
#         finally:
#             self._cleanup()
#
#     def _init_env(self):
#         if "virtualenv" in self._env_config.get("type"):
#             cmds = self._env_cmds()
#
#             # Extend commands with the ones specified by user
#             cmds.extend(
#                 python.user_install_cmd(self._env_config.get("init")))
#
#             print(cmds)
#
#             for c in cmds:
#                 cmd = split_cmd(c)
#                 print(cmd)
#                 try:
#                     subprocess.Popen(cmd)
#                 except OSError as e:
#                     raise ProcessError(e)
#
#     def _env_cmds(self):
#         env_dir = self._env_config.get("path")
#         env_run_dir = os.path.join(self.run_dir, env_dir)
#         return [
#             python.upgrade_pip(),
#             python.install_virtualenv(),
#             python.delete_env(env_run_dir),
#             "mkdir -p {}".format(env_run_dir),
#             python.init_virtualenv(env_run_dir),
#             python.activate_env(env_run_dir)
#         ]
#

#
#     def _python_exe(self):
#         """ Checks if the 'environment' key is
#             set in the experiment configuration
#             and returns the path to the python3
#             binary
#
#         Returns:
#             str -- path to python executable
#         """
#         if self._env_config:
#             if "virtualenv" in self._env_config.get("type"):
#                 path = os.path.join(
#                     os.path.abspath(self._env_config.get("path")),
#                     "bin/python3"
#                 )
#                 return path
#             # Add another type of environment here.
#         return sys.executable
#
#


def _to_dict(dict_values):
    return {x["key"]: x["value"] for x in dict_values}


#
#
# def _init_cmd_env(gpus):
#     env = utils.safe_osenv()
#     env["LOG_LEVEL"] = _log_level()
#     env["CMD_DIR"] = os.getcwd()
#     if gpus is not None:
#         log.info(
#             "Limiting available GPUs (CUDA_VISIBLE_DEVICES) to: %s",
#             gpus or "<none>")
#         env["CUDA_VISIBLE_DEVICES"] = gpus
#     return env
#
#
# def _log_level():
#     try:
#         return os.environ["LOG_LEVEL"]
#     except KeyError:
#         return str(logging.getLogger().getEffectiveLevel())
#
#
# def _create_parameter_list(config_parameters):
#     return [{
#         "key": p,
#         "value": config_parameters[p].get("value")
#     } for p in config_parameters if config_parameters[p].get("value")]
#
#
# def _sort_resolved(resolved):
#     return {
#         name: sorted(files) for name, files in resolved.items()
#     }
#
#
""" Command
"""


def split_cmd(main):
    if isinstance(main, list):
        return main
    return command.shlex_split(main or "")


def escape_quotes(s):
    return command.shlex_quotes(s)


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
