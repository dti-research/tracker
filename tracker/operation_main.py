# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" "External" script to be invoked by tracker.operation.run
    It is run by: `python3 -um tracker.operation_main {main}`
"""

import logging
import os
import sys
import warnings

from tracker.utils import python

log = logging.getLogger(__name__)

__argv0 = sys.argv


def main():
    _init_sys_path()
    _init_warnings()

    sourcecode_root = os.path.join(os.getcwd(), ".tracker/sourcecode")
    script = os.path.join(sourcecode_root, __argv0[1])

    python.exec_script(script)


def _init_sys_path():
    if os.getenv("SCRIPT_DIR") is not None:
        print(os.getenv("SCRIPT_DIR"))
        sys.path[0] = os.getenv("SCRIPT_DIR")


def _init_warnings():
    if log.getEffectiveLevel() > logging.DEBUG:
        warnings.simplefilter("ignore", Warning)
        warnings.filterwarnings("ignore", message="numpy.dtype size changed")
        warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        if log is None or log.getEffectiveLevel() <= logging.DEBUG:
            raise
        import traceback
        exc_lines = traceback.format_exception(*sys.exc_info())
        if len(exc_lines) < 3 or len(__argv0) < 2:
            # Assertion failure, but we want to be defensive in
            # deference to the actual error.
            raise
        # Print exception start with mod (argv[0])
        filtered_exc_lines = []
        mod_path = __argv0[1]
        for line in exc_lines[1:]:
            if filtered_exc_lines or mod_path in line:
                filtered_exc_lines.append(line)
        if not filtered_exc_lines:
            raise
        sys.stderr.write(exc_lines[0])
        for line in filtered_exc_lines:
            sys.stderr.write(line)
        sys.exit(1)
