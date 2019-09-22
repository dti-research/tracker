# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to manage YAML
"""


def encode_yaml(val):
    import ruamel.yaml as yaml
    encoded = yaml.safe_dump(
        val,
        default_flow_style=False,
        indent=2)
    if encoded.endswith("\n...\n"):
        encoded = encoded[:-4]
    return encoded
