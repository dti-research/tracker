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
import platform
import subprocess

import six

from .cli import error

PLATFORM = platform.system()

OS_ENVIRON_BLACKLIST = set([])


def safe_make_dir(d):
    d = os.path.realpath(d)
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def safe_listdir(path):
    try:
        return os.listdir(path)
    except OSError:
        return []


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


def find_apply(funs, *args, **kw):
    for f in funs:
        result = f(*args)
        if result is not None:
            return result
    return kw.get("default")


def try_read(path, default=None, apply=None):
    try:
        f = open(path, "r")
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise
        return default
    else:
        out = f.read()
        if apply:
            if not isinstance(apply, list):
                apply = [apply]
            for f in apply:
                out = f(out)
        return out


def which(cmd):
    which_cmd = "where" if PLATFORM == "Windows" else "which"
    devnull = open(os.devnull, "w")
    try:
        out = subprocess.check_output([which_cmd, cmd], stderr=devnull)
    except subprocess.CalledProcessError:
        return None
    else:
        return out.strip().decode("utf-8")


def safe_osenv():
    return {
        name: val
        for name, val in os.environ.items()
        if name not in OS_ENVIRON_BLACKLIST
    }


def check_env(env):
    for name, val in env.items():
        if not isinstance(name, six.string_types):
            raise ValueError("non-string env name %r" % name)
        if not isinstance(val, six.string_types):
            raise ValueError("non-string env value for '%s': %r" % (name, val))


def kill_process_tree(pid, force=False, timeout=None):
    import psutil
    import signal
    if force:
        sig = signal.SIGKILL
    else:
        sig = signal.SIGTERM
    root = psutil.Process(pid)
    procs = [root] + root.children(recursive=True)
    for proc in procs:
        proc.send_signal(sig)
    return psutil.wait_procs(procs, timeout=timeout)
