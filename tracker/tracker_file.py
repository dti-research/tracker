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
from tracker.utils import cli


NAME = "tracker.yaml"


class TrackerFile():

    def __init__(self, path=None):
        self._tracker_home = path or config.get_tracker_home()
        self._tracker_file = os.path.join(self._tracker_home, NAME)
        self._data = self._read()

    def _read(self):
        try:
            f = open(self._tracker_file, "r")
        except FileNotFoundError:
            self._create_tracker_home_file()
            self._read()
        except IOError:
            raise KeyError
        else:
            return yaml.safe_load(f)

    def _write(self, data=None):
        try:
            f = open(self._tracker_file, "w")
        except IOError:
            raise KeyError
        else:
            return yaml.safe_dump(data
                                  or self._data, f, default_flow_style=False)

    def get_tracker_file(self):
        return self._tracker_file

    def get(self, name, default=None):
        try:
            val = self._data[name]
        except KeyError:
            return default
        else:
            return val if val is not None else default

    def get_raw_data(self):
        return self._data

    def add_project(self, project):
        """Adds project to the global Tracker file

        Arguments:
            project {<dict>} -- project dictionary
        """
        if self._data is None:
            self._data = {}

        if "projects" not in self._data or self._data["projects"] is None:
            self._data["projects"] = []

        project_name = list(project.keys())[0]
        for d in self._data["projects"]:
            if project_name in d:
                cli.error("A project of that name ('{}') already exists!"
                          .format(project_name))

        # if project in self._data["projects"]:
        #     cli.error("Project: '{}' already exists!".format(project))

        self._data["projects"].append(project)
        self._write()

    def remove_project(self, project_name):
        """Removes the project to the global Tracker file

        Arguments:
            project {<str>} -- project name
        """
        self._data["projects"] = [
            d for d in self._data["projects"] if project_name not in d]
        self._write()
    
    def _create_tracker_home_file(self):
        open(self._tracker_file, 'a').close()