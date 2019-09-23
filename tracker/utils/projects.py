# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to locate tracker projects
"""

from tracker.tracker_file import TrackerFile


def get_project_names():
    """Searches for Tracker projects at the Tracker home configuration file

    Returns:
        <list> -- List of project names
    """

    trackerfile = TrackerFile()

    return [key for (key, value) in trackerfile.get("projects").items()]


def get_project_dirs():
    trackerfile = TrackerFile()

    data = trackerfile.get_raw_data()

    return [data["projects"][d]["path"] for d in data["projects"]]


def get_project_dir_by_name(name):
    trackerfile = TrackerFile()

    data = trackerfile.get_raw_data()

    return data["projects"][name]["path"]
