# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to load project configuration file
"""

import glob
import ruamel.yaml as yaml


def load(filepath):
    """ Load a configuration file.
    Args:
        filepath (str): -
    Returns:
        config_dict (dict): -
    """

    # TODO: Check if yaml or json

    # Read YAML experiment definition file
    with open(filepath, 'r') as stream:
        config_dict = yaml.load(stream, Loader=yaml.Loader)
    return config_dict


def set_value(dict, key, value):
    dict[key] = value


def get_config_files(ctx, args, incomplete):
    return [k for k in glob.glob('*.yaml') if incomplete in k]
