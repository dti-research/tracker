# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Helper class for reading the global Tracker file
"""

import os

import ruamel.yaml as yaml

from tracker.utils import config


NAME = "tracker.yaml"


class TrackerFile():

    def __init__(self, path=None):
        self._tracker_home = path or config.get_tracker_home()
        self._data = self._read()

    def _read(self):
        try:
            f = open(os.path.join(self._tracker_home, NAME), "r")
        except IOError:
            raise KeyError
        else:
            return yaml.safe_load(f)

    def get(self, name, default=None):
        try:
            val = self._data[name]
        except KeyError:
            return default
        else:
            return val if val is not None else default

    def get_raw_data(self):
        return self._data
