# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import io
from setuptools import setup

from tracker import __version__
version = __version__


with io.open('README.md', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

"""
with io.open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()
"""

requirements = [
    'click>=7.0',
    'cookiecutter>=1.4.0',
    'ruamel.yaml',
    'sh',
    'uuid',
    'astor>=0.8.0',
]

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
    entry_points={
        'console_scripts': [
            'tracker = tracker.main:main',
        ]
    },
    include_package_data=True,
    python_requires='>=3.6.*',
    install_requires=requirements,
    license='BSD',
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
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
