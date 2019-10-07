import logging
import os

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
