# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Show or manage experiments
"""

import click

from tracker.utils import click_utils

from .experiments_cmds.create import create
from .experiments_cmds.run import run


@click.group(invoke_without_command=True, cls=click_utils.Group)

@click.pass_context

def experiments(ctx, **kw):
    """Show or manage experiments.
    If `COMMAND` is omitted, lists experiments. Refer to ``tracker
    experiments list --help`` for more information on the `list` command.
    """
    # if not ctx.invoked_subcommand:
    #    ctx.invoke(list_runs, **kw)
    # else:
    if _params_specified(kw):
        # TODO: It'd be nice to move kw over to the subcommand.
        print(
            "options cannot be listed before command ('%s')"
            % ctx.invoked_subcommand)


def _params_specified(kw):
    return any((kw[key] for key in kw))


experiments.add_command(create)
experiments.add_command(run)
