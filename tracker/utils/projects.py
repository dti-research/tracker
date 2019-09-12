# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to locate tracker projects
"""

import os

_prefix = "TRACKER_"
_suffix = "_DIR"


def get_all():
    """Searches for Tracker projects by environment variables
       and returns their names.

    Returns:
        list -- List of project names
    """

    projects = []

    for key in os.environ.keys():
        if key.startswith(_prefix) and key.endswith(_suffix):
            projects.append(key.replace(_prefix, '').replace(_suffix, ''))

    return projects


def get_dir(name):
    return os.environ[_prefix + name + _suffix]
