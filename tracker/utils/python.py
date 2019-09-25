# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Helper functions for parsing python scripts through AST

    Workflow:
    - Determine if python should be loaded as module or run as script
    - python_util.exec_script(path, globals)

"""
