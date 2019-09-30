# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to change directory into Tracker projects
"""

import logging
import os

import click

from tracker.utils import cli, click_utils, projects

log = logging.getLogger(__name__)


def get_project_names(ctx, args, incomplete):
    return [k for k in projects.get_project_names() if incomplete in k]


@click.command("cd")

@click.argument(u'project_name', type=click.STRING,
                autocompletion=get_project_names)

@click.pass_context
@click_utils.use_args


def cd(ctx, args):
    """Change directory into any project created by Tracker.
       Lists all projects defined under the `projects` key in the
       Tracker home configuration file (default placed: ~/.tracker/)
    """

    log.debug("Searching for projects")

    # Retrieve project directory by its name
    project_dir = projects.get_project_dir_by_name(args.project_name)

    if not os.path.isdir(project_dir):
        cli.error("No such directory: {}".format(project_dir))
    else:
        try:
            os.chdir(project_dir)
            os.system("/bin/bash")
        except OSError as e:
            cli.error(e)
