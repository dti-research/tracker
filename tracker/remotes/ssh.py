# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import sys

import click

from tracker import remote as remotelib
from tracker import run as runlib
from tracker.utils import utils

from . import ssh_util


class SSHRemote(remotelib.Remote):

    def __init__(self, name, config):
        self.name = name
        self._host = config["host"]
        self.port = config.get("port")
        self.user = config.get("user")
        self.private_key = config.get("private-key")
        self.connect_timeout = config.get("connect-timeout")
        self.venv_path = config.get("venv-path") or config.get("tracker-env")
        self.tracker_home = self._init_tracker_home(config, self.venv_path)
        self.venv_activate = config.get("venv-activate")
        self.init = config.get("init")

    @staticmethod
    def _init_tracker_home(config, venv_path):
        tracker_home = config.get("tracker-home")
        if tracker_home is not None:
            return tracker_home
        if venv_path is None:
            return ".tracker"
        # return util.strip_trailing_sep(venv_path) + "/.tracker"

    @property
    def host(self):
        return self._host

    def status(self, verbose=False):
        ssh_util.ssh_ping(
            self.host,
            user=self.user,
            private_key=self.private_key,
            verbose=verbose,
            connect_timeout=self.connect_timeout,
            port=self.port)
        sys.stdout.write("%s (%s) is available\n" % (self.name, self.host))

    def start(self):
        raise remotelib.OperationNotSupported(
            "`start` is not supported for ssh remotes")

    def stop(self):
        raise remotelib.OperationNotSupported(
            "`stop` is not supported for ssh remotes")

    def which(self, cmd):
        which_cmd = "where" if utils.PLATFORM == "Windows" else "which"
        return ssh_util.ssh_output(
            self.host, [which_cmd + " " + cmd],
            user=self.user,
            private_key=self.private_key,
            connect_timeout=self.connect_timeout,
            port=self.port)

    def create_cmd(self, cmd):
        return ssh_util.get_ssh_cmd(
            self.host, cmd,
            user=self.user,
            private_key=self.private_key,
            connect_timeout=self.connect_timeout,
            port=self.port)

    def run_op(self, **opts):
        # print(opts)
        # {'background': False, 'experiment': 'cnn_test',
        # 'gpus': None, 'no_gpus': False, 'n_trials': None,
        # 'optimize': False, 'optimizer': None, 'random_seed': None}

        self._init_run()
        self._tracker_cmd("ls")

        run_id = runlib.mkid()
        return run_id
        # with util.TempDir(prefix="guild-remote-pkg-") as tmp:
        #     _build_package(tmp.path)
        #     remote_run_dir = self._init_remote_run(tmp.path, opspec, restart)
        # self._start_op(remote_run_dir, opspec, flags, **opts)
        # run_id = os.path.basename(remote_run_dir)
        # if no_wait:
        #     return run_id
        # try:
        #     self._watch_started_op(remote_run_dir)
        # except KeyboardInterrupt:
        #     raise remotelib.RemoteProcessDetached(run_id)
        # else:
        #     return run_id

    def _init_run(self):
        src = "/home/nily/Desktop/ast_test/src"  # HACK
        host_dest = "/home/dti/Desktop"  # HACK
        ssh_util.rsync_copy_to(
            src, self.host, host_dest,
            user=self.user,
            private_key=self.private_key,
            port=self.port)

    def _tracker_cmd(self, name, args=None, env=None):
        cmd_lines = ["set -e"]
        # cmd_lines.extend(self._env_activate_cmd_lines())
        cmd_lines.extend(self._set_columns())
        # if env:
        #     cmd_lines.extend(self._cmd_env(env))
        # cmd_lines.append("tracker %s %s" % (name, " ".join(args)))
        cmd_lines.append("tracker %s" % (name))
        cmd = "; ".join(cmd_lines)
        self._ssh_check_call(cmd)

    def _ssh_check_call(self, cmd):
        ssh_util.ssh_cmd(
            self.host, [cmd],
            user=self.user,
            private_key=self.private_key,
            connect_timeout=self.connect_timeout,
            port=self.port)

    @staticmethod
    def _set_columns():
        w, _h = click.get_terminal_size()
        return ["export COLUMNS=%i" % w]
