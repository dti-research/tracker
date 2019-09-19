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


log = logging.getLogger(__name__)


@click.command("list")

@click.pass_context

def list_remotes(ctx):
    """ Lists possible remotes
    """

    log.info("List remotes")
