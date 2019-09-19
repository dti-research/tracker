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
    return [k for k in projects.get_all() if incomplete in k]


@click.command("cd")

# Path the project configuration file (*.yaml/*.json)
@click.argument(u'project_name', type=click.STRING,
                autocompletion=get_project_names)

@click.pass_context
@click_utils.use_args


def cd(ctx, args):
    """Change directory into any project created by Tracker.
       Searches for environment variables starting with
       'TRACKER' and ends with 'DIR' as defined in the
       `.env` file in the root directory of the Tracker
       project.
    """

    log.debug("Searching for environment variables")

    # Retrieve project directory by its name specified in environment variables
    project_dir = projects.get_dir(args.project_name)

    if not os.path.isdir(project_dir):
        cli.error("No such directory: {}".format(project_dir))
    else:
        os.chdir(project_dir)
        os.system("/bin/bash")
