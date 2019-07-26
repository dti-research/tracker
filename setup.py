# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import io
from setuptools import setup

from pkg_resources import Distribution as PkgDist
from pkg_resources import PathMetadata

from tracker import __version__
version = __version__


with io.open('README.md', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [
    'click>=7.0'
]

#tracker_dist_basename = "tracker.dist-info"
#
#def tracker_dist_info():
#    metadata = PathMetadata(".", tracker_dist_basename)
#    dist = PkgDist.from_filename(tracker_dist_basename, metadata)
#    assert dist.project_name == "tracker", dist
#    entry_points = {
#        group: [str(ep) for ep in eps.values()]
#        for group, eps in dist.get_entry_map().items()
#    }
#    return dist._parsed_pkg_info, entry_points
#
##def tracker_packages():
##    return find_packages(exclude=["tracker.tests", "tracker.tests.*"])
#
#PKG_INFO, ENTRY_POINTS = tracker_dist_info()

setup(
    name='tracker',
    version=version,
    description=('A command-line utility that creates projects from project '
                 'templates, e.g. creating a Python package project from a '
                 'Python package project template.'),
    long_description=readme,
    author='Nicolai Anton Lynnerup',
    author_email='nily@dti.dk',
    url='https://github.com/dti-research/tracker',
    packages=[
        'tracker',
    ],
    package_dir={'tracker': 'tracker'},
    #entry_points=ENTRY_POINTS,
    entry_points={
        'console_scripts': [
            'tracker = tracker.main:main',
        ]
    },
    include_package_data=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=requirements,
    license='BSD',
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
    keywords=(
        'tracker, Python, projects, project templates, experiments, '
        'project directory, setup.py, package, statistics, '
        'packaging'
    ),
)

# 'Development Status :: 1 - Planning'
# 'Development Status :: 2 - Pre-Alpha'
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
# 'Development Status :: 6 - Mature'
# 'Development Status :: 7 - Inactive'
