# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility functions to assist serving
"""

import errno
import os
import subprocess
import sys

import click

from tracker.utils import click_utils


def host_and_port_options(fn):
    click_utils.append_params(fn, [
        click.Option(
            ("-h", "--host",), metavar="HOST",
            help="Name of host interface to listen on."),
        click.Option(
            ("-p", "--port",), metavar="PORT",
            help="Port to listen on.",
            type=click.IntRange(0, 65535)),
    ])
    return fn


def local_server_url(host, port):
    import socket
    if not host or host == "0.0.0.0":
        host = socket.gethostname()
        try:
            # Verify that configured hostname is valid
            socket.gethostbyname(host)
        except socket.gaierror:
            host = "localhost"
    return "http://{}:{}".format(host, port)


def free_port(start=None):
    import random
    import socket
    min_port = 49152
    max_port = 65535
    max_attempts = 100
    attempts = 0
    if start is None:
        def next_port(_p):
            return random.randint(min_port, max_port)
        port = next_port(None)
    else:
        def next_port(p):
            return p + 1
        port = start
    while True:
        if attempts > max_attempts:
            raise RuntimeError("too many free port attempts")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        try:
            sock.connect(('localhost', port))
        except socket.timeout:
            return port
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                return port
        else:
            sock.close()
        attempts += 1
        port = next_port(port)


def open_url(url):
    try:
        _open_url_with_cmd(url)
    except (OSError, URLOpenError):
        _open_url_with_webbrowser(url)


class URLOpenError(Exception):
    pass


def _open_url_with_cmd(url):
    if sys.platform == "darwin":
        args = ["open", url]
    else:
        args = ["xdg-open", url]
    with open(os.devnull, "w") as null:
        try:
            subprocess.check_call(args, stderr=null, stdout=null)
        except subprocess.CalledProcessError as e:
            raise URLOpenError(url, e)


def _open_url_with_webbrowser(url):
    import webbrowser
    webbrowser.open(url)
