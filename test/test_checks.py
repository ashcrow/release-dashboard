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
Tests to the main checks module.
"""
import pytest

from unittest import mock

from release_dashboard import checks


def mock_get_versions():
    """
    Mock version of AtomicStatusCheck.get_versions().
    """
    for x in range(1, 3):
        yield x


class TestAtomicStatusCheck:

    def test_init(self):
        """
        Check initialization doesn't require any variables but uses
        them when passed in.
        """
        # With no input
        asc = checks.AtomicStatusCheck()
        assert asc._logger is not None
        assert asc._compose_endpoint_tpl is not None
        assert asc._version_endpoint is not None
        # With logger
        sentry = mock.MagicMock('sentry')
        asc = checks.AtomicStatusCheck(logger=sentry)
        assert asc._logger is sentry
        # With compose_endpoint_tpl
        asc = checks.AtomicStatusCheck(compose_endpoint_tpl=sentry)
        assert asc._compose_endpoint_tpl is sentry
        # With version_endpoint
        asc = checks.AtomicStatusCheck(version_endpoint=sentry)
        assert asc._version_endpoint is sentry

    def test_versions(self):
        """
        Verify the versions property returns data from get_versions().
        """
        asc = checks.AtomicStatusCheck()
        asc.get_versions = mock_get_versions
        assert asc.versions == [1, 2]

    def test_has_version(self):
        """
        Ensure has_version returns True when the version is in the list.
        """
        asc = checks.AtomicStatusCheck()
        asc.get_versions = mock_get_versions
        assert asc.has_version(1) is True
        assert asc.has_version(999) is False

    def test_verify_compose_status(self):
        """
        Ensure compose status is read and handled properly.
        """
        with mock.patch('requests.get') as _get:
            # Good response, good code. Should be True.
            _get.return_value = mock.MagicMock(
                text='FINISHED\n', status_code=200)
            asc = checks.AtomicStatusCheck()
            assert asc.verify_compose_status('version') is True

            # Bad response, good code. Should be False.
            _get.return_value = mock.MagicMock(
                text='somethingelse\n', status_code=200)
            asc = checks.AtomicStatusCheck()
            assert asc.verify_compose_status('version') is False

            # Bad code, good data. Should be False
            _get.return_value = mock.MagicMock(
                text='FINISHED\n', status_code=404)
            asc = checks.AtomicStatusCheck()
            assert asc.verify_compose_status('version') is False

    def test_get_versions(self):
        """
        Verify that the right information is returned as versions.
        """
        # Read the fake list of versions
        with open('test/versions.html', 'r') as fobj:
            content = fobj.read()

        with mock.patch('requests.get') as _get:
            # Verify we have two versions
            _get.return_value = mock.MagicMock(
                text=content, status_code=200)
            versions = checks.AtomicStatusCheck().get_versions()
            version_list = [x for x in versions]
            assert len(version_list) == 2
            assert 'Fedora-Atomic-27-20180213.0' in version_list
            assert 'Fedora-Atomic-27-20180213.1' in version_list

            # No data, we should have no versions
            _get.return_value = mock.MagicMock(
                text='', status_code=200)
            versions = checks.AtomicStatusCheck().get_versions()
            version_list = [x for x in versions]
            assert len(version_list) == 0

            # Bad response, we should have no versions
            _get.return_value = mock.MagicMock(
                text=content, status_code=500)
            versions = checks.AtomicStatusCheck().get_versions()
            version_list = [x for x in versions]
            assert len(version_list) == 0
