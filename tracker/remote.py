# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

"""Contains template class for remote types.
"""

import click

from tracker.utils import cli
from tracker.utils import click_utils
from tracker.utils import config


class NoSuchRemote(ValueError):
    pass


class UnsupportedRemoteType(ValueError):
    pass


class MissingRequiredConfig(ValueError):
    pass


class OperationNotSupported(Exception):
    pass


class Down(Exception):
    pass


class OperationError(Exception):
    pass


class RemoteProcessError(Exception):

    def __init__(self, exit_status, cmd, output):
        super(RemoteProcessError, self).__init__(exit_status, cmd, output)
        self.exit_status = exit_status
        self.cmd = cmd
        self.output = output

    @classmethod
    def from_called_process_error(cls, e):
        return cls(e.returncode, e.cmd, e.output)


class RunFailed(Exception):

    def __init__(self, remote_run_dir):
        super(RunFailed, self).__init__(remote_run_dir)
        self.remote_run_dir = remote_run_dir


class RemoteProcessDetached(Exception):
    pass


class RemoteConfig(dict):
    def __getitem__(self, key):
        try:
            return super(RemoteConfig, self).__getitem__(key)
        except KeyError:
            raise MissingRequiredConfig(key)


class Remote():
    name = None

#    def push(self, runs, delete=False):
#        raise NotImplementedError()
#
#    def pull(self, runs, delete=False):
#        raise NotImplementedError()

    def status(self, verbose=False):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

#    def reinit(self):
#        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def which(self, cmd):
        raise NotImplementedError()

    def copy_src_to_host(self, src, host):
        raise NotImplementedError()

    def create_cmd(self, cmd):
        raise NotImplementedError()

#     @staticmethod
#     def get_stop_details():
#         return None
#
#     def run_op(self, opspec, flags, restart, no_wait, **opts):
#         raise NotImplementedError()
#
#     def list_runs(self, verbose=False, **filters):
#         raise NotImplementedError()
#
#     def filtered_runs(self, **filters):
#         raise NotImplementedError()
#
#     def one_run(self, run_id_prefix, attrs):
#         raise NotImplementedError()
#
#     def watch_run(self, **opts):
#         raise NotImplementedError()
#
#     def delete_runs(self, **opts):
#         raise NotImplementedError()
#
#     def restore_runs(self, **opts):
#         raise NotImplementedError()
#
#     def purge_runs(self, **opts):
#         raise NotImplementedError()
#
#     def label_runs(self, **opts):
#         raise NotImplementedError()
#
#     def run_info(self, **opts):
#         raise NotImplementedError()
#
#     def check(self, **opts):
#         raise NotImplementedError()
#
#     def stop_runs(self, **opts):
#         raise NotImplementedError()
#
#     def list_files(self, **opts):
#         raise NotImplementedError()
#
#     def diff_runs(self, **opts):
#         raise NotImplementedError()


def remote_op(op, prompt, default_resp, args):
    if not args.yes:
        cli.out(prompt)
    if args.yes or cli.confirm("Continue?", default_resp):
        try:
            op()
        except OperationNotSupported as e:
            cli.error(e)
        except OperationError as e:
            cli.error(e)


def remote_arg(fn):
    """`REMOTE` is the name of a configured remote. Use ``tracker remotes``
    to list available remotes.

    For information on configuring remotes, see ``tracker remotes
    --help``.

    """
    click_utils.append_params(fn, [
        click.Argument(("remote",), autocompletion=config.get_remote_names)
    ])
    return fn


def remote_for_args(args):
    assert args.remote, args
    try:
        return for_name(args.remote)
    except NoSuchRemote:
        cli.error(
            "remote '%s' is not defined\n"
            "Show remotes by running 'tracker remotes' or "
            "'tracker remotes --help' for more information."
            % args.remote)
    except UnsupportedRemoteType as e:
        cli.error(
            "remote '%s' in ~/.tracker/tracker.yaml has unsupported "
            "type: %s" % (args.remote, e.args[0]))
    except MissingRequiredConfig as e:
        cli.error(
            "remote '%s' in ~/.tracker/tracker.yaml is missing required "
            "config: %s" % (args.remote, e.args[0]))


def for_name(name):
    user_config = config.get_user_config()
    remotes = user_config.get("remotes", {})
    try:
        remote = remotes[name]
    except KeyError:
        raise NoSuchRemote(name)
    else:
        remote_config = RemoteConfig(remote)
        remote_type = remote_config["type"]
        return _for_type(remote_type, name, remote_config)


def _for_type(remote_type, name, config):
    if remote_type == "ssh":
        from tracker.remotes import ssh
        cls = ssh.SSHRemote
    else:
        raise UnsupportedRemoteType(remote_type)
    remote = cls(name, config)
    return remote
