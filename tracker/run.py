# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Helper class for trials (named run in command)
"""

import os
import uuid

import ruamel.yaml as yaml

from tracker import utils
from tracker.utils import yaml as yamllib


class Run():

    __properties__ = [
        "id",
        "path",
        "short_id",
        "pid",
        "status",
        "timestamp",
    ]

    def __init__(self, id, path):
        self.id = id
        self.path = path
        self._tracker_dir = os.path.join(self.path, ".tracker")

    @property
    def short_id(self):
        return self.id[:8]

    @property
    def dir(self):
        """Alias for path attr."""
        return self.path

    @property
    def pid(self):
        lockfile = self.tracker_path("LOCK")
        try:
            raw = open(lockfile, "r").read(10)
        except (IOError, ValueError):
            return None
        else:
            try:
                return int(raw)
            except ValueError:
                return None

    @property
    def status(self):
        if os.path.exists(self.tracker_path("LOCK.remote")):
            return "running"
        elif os.path.exists(self.tracker_path("PENDING")):
            return "pending"
        else:
            if self.has_attr("exit_status.remote"):
                return self._remote_exit_status()
            else:
                return self._local_status()

    @property
    def remote(self):
        remote_lock_file = self.tracker_path("LOCK.remote")
        return utils.utils.try_read(remote_lock_file, apply=str.strip)

    @property
    def timestamp(self):
        return utils.utils.find_apply([
            lambda: self.get("started"),
            lambda: self.get("initialized"),
            lambda: None
        ])

    def _remote_exit_status(self):
        status = self.get("exit_status.remote")
        if status == 0:
            return "completed"
        elif status == 2:
            return "terminated"
        else:
            return "error"

    def _local_status(self):
        pid = self.pid  # side-effect, read once
        if pid is None:
            exit_status = self.get("exit_status")
            if exit_status is None:
                return "error"
            elif exit_status == 0:
                return "completed"
            elif exit_status < 0:
                return "terminated"
            else:
                return "error"
        elif utils.pid.pid_exists(pid):
            return "running"
        else:
            return "terminated"

    def get(self, name, default=None):
        try:
            val = self[name]
        except KeyError:
            return default
        else:
            return val if val is not None else default

    def attr_names(self):
        return sorted(utils.utils.safe_listdir(self._attrs_dir()))

    def has_attr(self, name):
        return os.path.exists(self._attr_path(name))

    def iter_attrs(self):
        for name in self.attr_names():
            try:
                yield name, self[name]
            except KeyError:
                pass

    def __getitem__(self, name):
        try:
            f = open(self._attr_path(name), "r")
        except IOError:
            raise KeyError(name)
        else:
            return yaml.safe_load(f)

    def _attr_path(self, name):
        return os.path.join(self._attrs_dir(), name)

    def _attrs_dir(self):
        return os.path.join(self._tracker_dir, "attrs")

    def __repr__(self):
        return "<tracker.run.Run '%s'>" % self.id

    def init_skeleton(self):
        utils.utils.safe_make_dir(self.tracker_path("attrs"))
        if not self.has_attr("initialized"):
            self.write_attr("id", self.id)
            self.write_attr("initialized", utils.timestamp.timestamp())

    def tracker_path(self, *subpath):
        if subpath is None:
            return self._tracker_dir
        return os.path.join(*((self._tracker_dir,) + tuple(subpath)))

    def write_attr(self, name, val, raw=False):
        if not raw:
            val = self._encode_attr_val(val)
        with open(self._attr_path(name), "w") as f:
            f.write(val)
            f.close()

    @staticmethod
    def _encode_attr_val(val):
        return yamllib.encode_yaml(val)

    def del_attr(self, name):
        try:
            os.remove(self._attr_path(name))
        except OSError:
            pass

    def iter_files(self, all_files=False, follow_links=False):
        for root, dirs, files in os.walk(self.path, followlinks=follow_links):
            if not all_files and root == self.path:
                try:
                    dirs.remove(".tracker")
                except ValueError:
                    pass
            for name in dirs:
                yield os.path.join(root, name)
            for name in files:
                yield os.path.join(root, name)

    def iter_tracker_files(self, subpath):
        tracker_path = self.tracker_path(subpath)
        if os.path.exists(tracker_path):
            for root, dirs, files in os.walk(tracker_path):
                rel_root = os.path.relpath(root, tracker_path)
                if rel_root == ".":
                    rel_root = ""
                for name in dirs:
                    yield os.path.join(rel_root, name)
                for name in files:
                    yield os.path.join(rel_root, name)


def mkid():
    return uuid.uuid4().hex
