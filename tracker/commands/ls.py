# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to get a list of current Tracker projects
"""

import logging
import click

from tracker.utils import cli
from tracker.utils import projects as projectslib

log = logging.getLogger(__name__)


@click.command("ls")

@click.pass_context


def ls(ctx):
    """Lists all projects created by Tracker.
       Collects all projects defined in the `tracker.yaml`
       configuration file
    """

    projects = projectslib.get_project_names_and_dirs()
    cols = ["name", "path"]

    heading = {
        col_name: col_name.capitalize()
        for col_name in cols
    }

    data = [heading] + projects

    cli.table(data, cols)
