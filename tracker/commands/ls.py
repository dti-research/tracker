# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to get a list of current Tracker projects
"""

import os
import logging
import click

from tracker.utils import projects
from tracker.utils import print_lists

log = logging.getLogger(__name__)


@click.command("ls")

@click.pass_context


def ls(ctx):
    """Lists all projects created by Tracker.
       Searches for environment variables starting with
       'TRACKER' and ends with 'DIR' as defined in the
       `.env` file in the root directory of the Tracker
       project.
    """

    log.debug("Searching for environment variables")

    project_list = projects.get_all()
            

    if len(project_list) == 0:
        log.info("No Tracker projects found!")
        return 1
    else:
        log.debug("Listing project names and paths")

        # TODO: List projects by their names and not env.variables
        print_lists.print_two_coloumn(project_list)
