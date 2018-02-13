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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Various check classes and functions.
"""


import logging

import requests

from bs4 import BeautifulSoup


class AtomicStatusCheck:
    """
    Class for checking atomic statuses based on external resources.
    """

    def __init__(self, logger=None,
                 compose_endpoint_tpl=None, version_endpoint=None):
        """
        Initializes a new instance of AtomicStatusCheck.

        :param logger: An optional logger to use internally.
        :type logger: logging.Logger
        :param compose_endpoint_tpl: Optional template url for compose check.
        :type compose_endpoint_tpl: str
        :param version_endpoint: Optional version url for version list.
        :type version_endpoint: str
        """
        self._versions = []
        self._compose_endpoint_tpl = (
            'https://kojipkgs.fedoraproject.org/compose/twoweek/{}/STATUS')
        if compose_endpoint_tpl is not None:
            self._compose_endpoint_tpl = compose_endpoint_tpl
        self._version_endpoint = (
            'https://kojipkgs.fedoraproject.org/compose/twoweek/?C=M;O=D')
        if version_endpoint is not None:
            self._version_endpoint = version_endpoint
        if logger is not None:
            self._logger = logger
        else:
            self._logger = logging.getLogger('AtomicStatusCheck')

    @property
    def versions(self):
        """
        Property that lists all known versions.
        """
        if len(self._versions) == 0:
            self._logger.debug('No versions loaded. Loading from remote.')
            self._versions = [x for x in self.get_versions()]
            self._logger.info('Loaded %d versions', len(self._versions))
        else:
            self._logger.debug('Versions already loaded. Reusing.')
        return self._versions

    def verify_compose_status(self, version):
        """
        Verifies if a compose has finished.

        :param version: Version string to check.
        :type version: str
        :returns: True if the composes is finished, otherwise False
        :rtype: bool
        """
        url = self._compose_endpoint_tpl.format(version)
        self._logger.info('Verifying status via %s', url)
        resp = requests.get(url)
        if resp.status_code == 200:
            status = resp.text.lower()[:-1]
            self._logger.debug('Result from url: %s', resp.text)
            if status == 'finished':
                return True
        else:
            self._logger.warn(
                'Received a non 200 response: %d', resp.status_code)
        return False

    def get_versions(self):
        """
        Uses the version_endpoint to find all known versions as a generator.

        :returns: A generator that returns the next known version on iteration
        :rtype: generator
        """
        self._logger.info('Getting versions from %s', self._version_endpoint)
        resp = requests.get(self._version_endpoint)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for node in soup.find_all('a'):
                text = node.get_text()
                if text.startswith('Fedora-Atomic-'):
                    self._logger.debug('Found %s', text[:-1])
                    yield text[:-1]
        else:
            self._logger.warn(
                'Received a non 200 response: %d', resp.status_code)
            return []

    def has_version(self, version):
        """
        Checks a given version against the known versions from the
        version endpoint.

        :param version: Version string to check.
        :type version: str
        :returns: True if the version is known, otherwise False
        :rtype: bool
        """
        return version in self.versions


def example():  # pragma: no cover
    # Create a logger to pass in
    logger = logging.getLogger('AtomicStatusCheck')
    logger.setLevel(logging.DEBUG)
    logger.handlers = [logging.StreamHandler()]

    # Create an instance
    av = AtomicStatusCheck(logger=logger)

    # Get the first instance to verify a compose status
    first_version = next(av.get_versions())
    # Check the status and print something nice
    if av.verify_compose_status(first_version):
        print('Compose is ready')
    else:
        print('Compose is not done')
    # Check if a specific version exists. This should force
    # a population of the _version store
    print(av.has_version('Fedora-Atomic-27-20171123.0'))
    # Check a version that shouldn't exist. This should reuse
    # the _version store.
    print(av.has_version('Fedora-Atomic-27-20171123.3'))


if __name__ == '__main__':
    example()
