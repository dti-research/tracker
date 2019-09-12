# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to create a new ML project
"""

import os
import sh
import logging
import click
import ruamel.yaml as yaml

from tracker.utils import conf
from tracker.utils import click_utils

from cookiecutter.main import cookiecutter

log = logging.getLogger(__name__)


@click.command("create")

# Path the project configuration file (*.yaml/*.json)
@click.argument(u'configuration', type=click.STRING,
                autocompletion=conf.get_config_files)


@click.pass_context
@click_utils.use_args

def create(ctx, args):
    """Creates a new project based on a CONFIGURATION FILE.
       Pushes it subsequently to the chosen git repository.
    """

    # Load configuration file
    config_dict = conf.load(args.configuration)
    log.debug(yaml.dump(config_dict, default_flow_style=False))

    # Tell user what we're doing
    log.info("Creating a new project based on {}"
             .format(config_dict['template']))

    # Create directory if it does not exist
    output_dir = config_dict['project']['output_dir']
    if not os.path.exists(output_dir):
        log.warn("Output directory does not exist. Creating it.")
        os.makedirs(output_dir)

    # Set project directory environment variable
    config_dict["project"]["project_dir"] = \
        os.path.join(os.path.abspath(output_dir),
                     config_dict['project']['project_name'].lower())

    # Invoke the Cookiecutter project template
    cookiecutter(config_dict['template'], no_input=True,
                 overwrite_if_exists=config_dict['overwrite_if_exists'],
                 extra_context=config_dict['project'], output_dir=output_dir)

    # Check if we should assist user with git management
    if 'repo' not in config_dict['project']:
        # TODO: If not, set environment variable and do not assist user in
        # managing trials..

        # Could we prompt user for repo?

        log.warn("There's no git repository in the configuration file! "
                 "As a result, your experiments will not be linked to git.")
    else:
        # Init git repo locally
        repo_name = config_dict['project']['project_name'].lower()
        log.info("Initialising git repo '{}'.".format(repo_name))

        git = sh.git.bake(_cwd=os.path.join(output_dir, repo_name))
        git.init()

        # Add remote URL
        git.remote.add.origin(config_dict['project']['repo'])
        log.debug("git remote -v \n{}".format(git.remote('-v')))

        # DEBUG: Print git status
        log.debug(git.status())

        # Add all files
        git.add('-A')

        # DEBUG: Print git status
        log.debug(git.status())

        # Commit and push
        git.commit(m='Initial commit')
        git.push("--set-upstream", "origin", "master")
