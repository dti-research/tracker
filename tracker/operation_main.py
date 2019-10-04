import logging
import os
import sys
import warnings

log = logging.getLogger(__name__)

__argv0 = sys.argv


def main():

    _init_sys_path()
    # _init_logging()
    _init_warnings()
    print("cwd: {}".format(os.getcwd()))
    print("sys.path:{}".format(os.path.pathsep.join(sys.path)))
    # arg1, rest_args = _parse_args()
    # _apply_plugins()
    # _try_module(arg1, rest_args)


def _init_sys_path():
    if os.getenv("SCRIPT_DIR") is not None:
        print(os.getenv("SCRIPT_DIR"))
        sys.path[0] = os.getenv("SCRIPT_DIR")

# def _init_logging():
#     level = int(os.getenv("LOG_LEVEL", logging.WARN))
#     format = os.getenv("LOG_FORMAT", "%(levelname)s: [%(name)s] %(message)s")


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
