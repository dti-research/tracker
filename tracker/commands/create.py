# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to create a new ML project
"""

import os
import logging
import click
import ruamel.yaml as yaml

from tracker.utils import conf
from tracker.utils import click_utils

from cookiecutter.main import cookiecutter
from git import Repo, Commit

log = logging.getLogger(__name__)


@click.command("create")

# Path the project configuration file (*.yaml/*.json)
@click.argument(u'configuration', type=click.STRING,
                autocompletion=conf.get_config_files)


@click.pass_context
@click_utils.use_args

def create(ctx, args):
    """Creates a new project
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

    # Invoke the Cookiecutter project template
    cookiecutter(config_dict['template'], no_input=True,
                 overwrite_if_exists=config_dict['overwrite_if_exists'],
                 extra_context=config_dict['project'], output_dir=output_dir)

    # Init git repo locally
    #repo_name = config_dict['project']['project_name'].lower()
    #log.info("Initialising git repo '{}'.".format(repo_name))
    
    #repo = Repo.init(os.path.join(output_dir,repo_name))
    #git = repo.git

    # Setup remote
    
    #o = repo.remotes.origin
    #print(repo.remotes)
    #origin = repo.create_remote('origin', repo.remotes.origin.url)


    # Add and commit all files
    #repo.index.add(repo.untracked_files)
    #repo.index.commit("initial commit")


    #log.debug(repo.untracked_files)
    #print(git.__version__)
    #log.debug(repo.remotes.origin.url)

    # Push to remote
    #origin.push()