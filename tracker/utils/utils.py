# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to manage files and directories
"""

import errno
import os

from .cli import error


def safe_make_dir(d):
    d = os.path.realpath(d)
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_validated_dir_path(path, abs=False, create=False):
    path = os.path.expanduser(path)
    if abs:
        path = os.path.abspath(path)
    if not os.path.exists(path):
        if create:
            safe_make_dir(path)
        else:
            error("directory '%s' does not exist" % path)
    if not os.path.isdir(path):
        error("'%s' is not a directory" % path)
    return path
