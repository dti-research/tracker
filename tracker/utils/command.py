# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

"""Utility code to manage commands given to terminal
"""

import shlex


def shlex_split(s):
    # If s is None, this call will block (see
    # https://bugs.python.org/issue27775)
    s = s or ""
    return shlex.split(s)


def shlex_quotes(s):
    s = s or ""
    return shlex.quote(s)
