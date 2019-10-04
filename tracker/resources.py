# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import logging
import os
import zipfile

import requests

log = logging.getLogger(__name__)


class ResourceError(Exception):
    pass


class Resource():

    def __init__(self, resource, output_dir=None):
        self._resource = resource
        self._output_dir = output_dir

    def resolve(self):
        if self._output_dir is None:
            self._output_dir = self._resource["output"]

        # TODO: Check if select is already present

        # print(self._resource)

        url = self._resource["url"]

        zip_file = url.rsplit('/', 1)[-1]

        log.debug("Checking if .zip files exists...")

        # Check if folder contains the zip files otherwise download them
        zip_file_path = os.path.join(self._output_dir, zip_file)
        if not os.path.exists(zip_file_path):
            # Download zip file
            download_zip(url, zip_file_path)

            # Extract zip file
            extract_zip(zip_file_path, self._output_dir)


def resolve(resource_config):
    resolved = {}

    # Loop through the sources
    for res in _inline_resource(resource_config.get("sources")):
        res.resolve()

    return resolved
    # resolved = {}
    # for res in resources(dependencies, ctx):
    #     log.info("Resolving %s dependency", res.resdef.name)
    #     resolved_sources = res.resolve()
    #     log.debug(
    #         "resolved sources for %s: %r",
    #         res.dependency, resolved_sources)
    #     if not resolved_sources:
    #         log.warning("Nothing resolved for %s dependency",
    # res.resdef.name)
    #     resolved.setdefault(res.resdef.name, []).extend(resolved_sources)
    # return resolved


def _inline_resource(resource_config):
    return [Resource(res) for res in resource_config]


def download_zip(url, path):
    log.debug("[Warning] '" + path + "' No such file or directory")
    log.debug("   Downloading from: '" + url + "'")

    if "http_proxy" in os.environ:
        proxies = {
            'http': os.getenv('http_proxy'),
            'https': os.getenv('https_proxy'),
        }

        log.debug("Detected the following proxy settings:")
        log.debug(proxies)

        r = requests.get(url, proxies=proxies)
    else:
        r = requests.get(url)

    # Raise error if one comes up
    r.raise_for_status()

    # Save zip file
    with open(path, 'wb') as f:
        f.write(r.content)


def extract_zip(input_zip_file, output_dir):
    # Extract zip file
    log.debug("Extracting '" + input_zip_file + "'")
    zip_ref = zipfile.ZipFile(input_zip_file, 'r')
    zip_ref.extractall(output_dir)
    zip_ref.close()
