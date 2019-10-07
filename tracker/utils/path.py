import logging
import os
import shutil
import tempfile

from tracker.utils import config

log = logging.getLogger(__name__)


def path(*names):
    names = [name for name in names if name]
    return os.path.join(config.get_tracker_home(), *names)


def runs_dir():
    return path("runs")


def experiment_runs_dir(experiment_name):
    return os.path.join(
        path("experiments"),
        experiment_name)


class TempBase(object):

    def __init__(self, prefix="tracker-", suffix="", keep=False):
        self._prefix = prefix
        self._suffix = suffix
        self._keep = keep
        self.path = self._init_temp(self._prefix, self._suffix)

    def __enter__(self):
        return self

    @staticmethod
    def _init_temp(prefix, suffix):
        raise NotImplementedError()

    def __exit__(self, *_exc):
        if not self._keep:
            self.delete()

    @staticmethod
    def delete():
        raise NotImplementedError()


class TempDir(TempBase):

    @staticmethod
    def _init_temp(prefix, suffix):
        return tempfile.mkdtemp(prefix=prefix, suffix=suffix)

    def delete(self):
        rm_temp_dir(self.path)


class TempFile(TempBase):

    @staticmethod
    def _init_temp(prefix, suffix):
        f, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(f)
        return path

    def delete(self):
        os.remove(self.path)


def rm_temp_dir(path):
    assert os.path.dirname(path) == tempfile.gettempdir(), path
    try:
        shutil.rmtree(path)
    except Exception as e:
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.exception("rmtree %s", path)
        else:
            log.error("error removing %s: %s", path, e)
