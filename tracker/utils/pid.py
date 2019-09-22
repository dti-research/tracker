# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to manage process IDs
"""

import logging

log = logging.getLogger(__name__)


def pid_exists(pid):
    try:
        import psutil
    except Exception as e:
        log.warning("Cannot get stat for pid %s: %s", pid, e)
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.exception("Importing psutil")
        return False
    return psutil.pid_exists(pid)
