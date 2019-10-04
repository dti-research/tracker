# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Helper functions for parsing python scripts through AST
    and executing them as python scripts
"""

import ast


def exec_script(filename):
    """Execute a Python script.

    This function can be used to execute a Python module as code
    rather than import it. Importing a module to execute it is not an
    option if importing has a side-effect of starting threads, in
    which case this function can be used.

    Reference:

    https://docs.python.org/2/library/threading.html#importing-in-threaded-code

    """
    src = open(filename, "r").read()
    tree = ast.parse(src, filename)

    code = compile(tree, filename, mode="exec")

    exec(code)
