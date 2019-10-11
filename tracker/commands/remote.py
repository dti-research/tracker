# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to manage remotes
"""


import click

from tracker.utils import click_utils

from .remote_start import remote_start
from .remote_status import remote_status
from .remote_stop import remote_stop


@click.group(cls=click_utils.Group)

def remote():
    """Manage remotes (start/stop/status).
    """

    # TODO: Add command to add new remotes at either project or
    #       at global level.


remote.add_command(remote_start)
remote.add_command(remote_status)
remote.add_command(remote_stop)
