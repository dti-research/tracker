# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Show and manage CUDA GPUs
"""

import click

from tracker.utils import click_utils

from .gpus_list import list_gpus


@click.group(invoke_without_command=True, cls=click_utils.Group)
@click.pass_context

def gpus(ctx, **kw):
    """ Show and manage NVIDIA GPUs.
        If `COMMAND` is omitted, lists GPUs. Refer to ``tracker
        gpus list --help`` for more information on the `list` command.
    """
    if not ctx.invoked_subcommand:
        ctx.invoke(list_gpus, **kw)
    else:
        if _params_specified(kw):
            print(
                "options cannot be listed before command ('%s')"
                % ctx.invoked_subcommand)


def _params_specified(kw):
    return any((kw[key] for key in kw))


gpus.add_command(list_gpus)

# TODO: Add ability to activate/deactive the use of specific GPUs as a
#       compliment to "...run --no-gpus" or "...run --gpus 1,2,3"
