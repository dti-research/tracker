# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to locate tracker projects
"""

from tracker.tracker_file import TrackerFile
from tracker.utils import cli
from tracker.utils import config


def is_cwd_project(cwd):
    raise NotImplementedError


def get_project_names_and_dirs():
    trackerfile = TrackerFile()
    projects = trackerfile.get("projects", {})

    if projects:
        data = [
            {
                "name": name,
                "path": r.get("path", ""),
            }
            for d in projects for name, r in d.items()
        ]
        return data
    else:
        cli.error("No projects specified in {}".format(
            config.get_user_config_path()))


def get_project_names():
    """Searches for Tracker projects at the Tracker home configuration file

    Returns:
        <list> -- List of project names
    """

    trackerfile = TrackerFile()

    projects = trackerfile.get("projects", {})

    project_names = []

    if projects:
        for d in projects:
            k, _ = list(d.items())[0]
            project_names.append(k)

    return project_names


def get_project_dir_by_name(name):
    trackerfile = TrackerFile()

    data = trackerfile.get("projects")

    for d in data:
        k, _ = list(d.items())[0]
        if name in k:
            path = d[k]["path"]

    return path
