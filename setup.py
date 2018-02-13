#!/usr/bin/env python3
#
# Copyright (C) 2018  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Source build and installation script.
"""

import pip

from setuptools import setup, find_packages


def extract_requirements(filename):
    requirements = []
    for x in pip.req.parse_requirements(
            filename, session=pip.download.PipSession()):
        if x.req:
            requirements.append(str(x.req))
        elif x.link:
            print('\nIgnoring {} ({})'.format(x.link.url, x.comes_from))
            print('To install it run: pip install {}\n'.format(x.link.url))
    return requirements


install_requires = extract_requirements('requirements.txt')
test_require = extract_requirements('test-requirements.txt')


setup(
    name='release_dashboard',
    version='0.0.1',
    description='Release dashboard used for the Fedora AH 2 week release',
    url='https://github.com/ashcrow/release-dashboard',
    license="GPLv3+",

    install_requires=install_requires,
    tests_require=test_require,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    package_data={},
    entry_points={
        'console_scripts': [
            'release-dashboard = release_dashboard.cli:main',
        ],
    }
)
