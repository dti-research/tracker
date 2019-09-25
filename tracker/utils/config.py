# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to load project configuration file
"""

import logging
import glob
import os

import ruamel.yaml as yaml

from tracker.utils import cli


log = logging.getLogger(__name__)

_cwd = None
_tracker_home = None
_user_config = None


def set_cwd(cwd):
    globals()["_cwd"] = cwd


def get_cwd():
    return _cwd or "."


def set_tracker_home(path):
    globals()["_tracker_home"] = path


def get_tracker_home():
    return (
        _tracker_home
        or os.getenv("TRACKER_HOME")
        or os.path.join(os.path.expanduser("~"), ".tracker"))


def get_user_config():
    path = get_user_config_path()
    config = _user_config
    if config is None or config.path != path:
        config = _Config(path)
        globals()["_user_config"] = config
    return config.read()


def get_user_config_path():
    try:
        local_user_config = os.path.join(get_cwd(), "tracker.yaml")
        if os.path.isfile(local_user_config):
            return local_user_config
        else:
            raise KeyError
    except KeyError:
        return os.path.join(os.path.expanduser("~"),
                            ".tracker",
                            "tracker.yaml")


def load(filepath):
    """ Load a configuration file.
    Args:
        filepath (str): -
    Returns:
        config_dict (dict): -
    """
    with open(filepath, 'r') as stream:
        config_dict = yaml.load(stream, Loader=yaml.Loader)
    return config_dict


def get_config_files(ctx, args, incomplete):
    return [k for k in glob.glob('*.yaml') if incomplete in k]


def get_remotes():
    remotes = get_user_config().get("remotes", {})
    if remotes:
        data = [
            {
                "name": name,
                "type": r.get("type", ""),
                "host": r.get("host", ""),
                "desc": r.get("description", ""),
            }
            for name, r in sorted(remotes.items())
        ]
        return data
    else:
        cli.error("No remotes specified in {}".format(
            get_user_config_path()))


def get_remote_names(ctx, args, incomplete):
    return [k['name'] for k in get_remotes() if incomplete in k['name']]


class _Config():

    def __init__(self, path):
        self.path = path
        self._data = None
        self._mtime = 0

    def read(self):
        if self._data is None or self._path_mtime() > self._mtime:
            self._data = self._parse()
            # _apply_config_inherits(self._data, self.path)
            self._mtime = self._path_mtime()
        return self._data

    def _path_mtime(self):
        try:
            return os.path.getmtime(self.path)
        except (IOError, OSError):
            return 0

    def _parse(self):
        try:
            f = open(self.path, "r")
        except IOError as e:
            if e.errno != 2:  # file not found
                log.warning(
                    "cannot read user config in %s: %s",
                    self.path, e)
        else:
            try:
                return yaml.safe_load(f) or {}
            except Exception as e:
                log.warning(
                    "error loading user config in %s: %s",
                    self.path, e)
        return {}
