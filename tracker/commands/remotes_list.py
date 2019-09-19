# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to list possible remotes
"""

import logging
import click

from tracker.utils import cli
from tracker.utils import config

log = logging.getLogger(__name__)


@click.command("list")
@click.pass_context
def list_remotes(ctx):
    """ Lists possible remotes
    """
    remotes = config.get_user_config().get("remotes", {})
    if remotes:
        data = [
            {
                "name": name,
                "type": r.get("type", ""),
                "host": r.get("host", ""),
                "desc": r.get("description", ""),
            }
            for name, r in sorted(remotes.items())
        ]
        cli.table(data, ["name", "type", "host", "desc"])
    else:
        cli.error("No remotes specified in {}".format(
            config.get_user_config_path()))
