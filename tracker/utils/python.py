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
import re
import os
import sys


PIP_CMD = "pip3"
BUILD_DIR = "build-env"


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


def sys_interpreters():
    import glob
    bin_dir = os.path.dirname(sys.executable)
    ret = []
    for path in glob.glob(os.path.join(bin_dir, "python*")):
        m = re.match(r"python([0-9\.]+)$", os.path.basename(path))
        if m:
            ret.append((path, m.group(1)))
    return ret


def find_interpreter(version_spec):
    import pkg_resources
    try:
        # Requirement.parse wants a package name, so we use 'python'
        # here, but anything would do.
        req = pkg_resources.Requirement.parse("python%s" % version_spec)
    except pkg_resources.RequirementParseError:
        raise ValueError(version_spec)
    python_interps = {ver: path for path, ver in sys_interpreters()}
    matching = list(req.specifier.filter(sorted(python_interps)))
    if matching:
        matching_ver = matching[0]
        return python_interps[matching_ver], matching_ver
    return None


def _pip_install(pkgs, sudo=False):
    sudo_part = "sudo -H " if sudo else ""
    pkgs_part = " ".join([_pkg_spec(pkg) for pkg in pkgs])
    # pipe to cat effectively disables progress bar
    return (
        "{sudo}{pip} install --upgrade {pkgs}"  # | cat
        .format(
            sudo=sudo_part,
            pip=PIP_CMD,
            pkgs=pkgs_part))


def _pkg_spec(pkg):
    if pkg.endswith(".txt"):
        return "-r {}".format(pkg)
    return pkg


def activate_env(path):
    return ". {}/bin/activate".format(path)


def upgrade_pip():
    return _pip_install(["pip"], sudo=True)


def install_virtualenv():
    return _pip_install(["virtualenv"], sudo=True)


def delete_env(path):
    return "rm -rf {}".format(path)


def init_virtualenv(path):
    return "python3 -m virtualenv {}".format(path)


def user_install_cmd(init_cmds):
    return init_cmds.split("\n")
