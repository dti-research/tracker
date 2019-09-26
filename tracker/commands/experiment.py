# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Manage experiments and conduct trials
"""

import click

from tracker.utils import click_utils

from .experiment_create import create
from .experiment_run import run


@click.group(cls=click_utils.Group)
@click.pass_context

def experiment(ctx, **kw):
    """Manage experiments and conduct trials
    """


def _params_specified(kw):
    return any((kw[key] for key in kw))


experiment.add_command(create)
experiment.add_command(run)
