# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to change directory into Tracker projects
"""

import logging
import shutil

import click

from tracker import tracker_file
from tracker.utils import cli, click_utils, projects

log = logging.getLogger(__name__)


def get_project_names(ctx, args, incomplete):
    return [k for k in projects.get_project_names() if incomplete in k]


@click.command("rm")

@click.argument(u'project_name', type=click.STRING,
                autocompletion=get_project_names)
@click_utils.no_prompt_option
@click.pass_context
@click_utils.use_args


def rm(ctx, args):
    """Change directory into any project created by Tracker.
       Lists all projects defined under the `projects` key in the
       Tracker home configuration file (default placed: ~/.tracker/)
    """

    # Prompt user for deletion of files on disk
    if args.yes or _confirm_rm(args):
        _rm_files(args)

    # Remove from global configuration file tracker.yaml
    trackerfile = tracker_file.TrackerFile()
    trackerfile.remove_project(args.project_name)


def _rm_files(args):
    # Retrieve project directory by its name
    project_dir = projects.get_project_dir_by_name(args.project_name)

    # Delete folder
    shutil.rmtree(project_dir)


def _confirm_rm(args):
    prompt = (
        "You are about to delete {}. "
        "Do you want to delete all project files on the disk?"
        .format(
            args.project_name)
    )
    return cli.confirm(prompt, default=False)
