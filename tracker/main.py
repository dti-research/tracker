# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

"""
Main entry point for the `tracker` command.
"""

import os

def tracker(test):
    os.system("cat {}".format(test))
    print(test)