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
Pagure tracker tests.
"""

import os

import libpagure
import pytest

from unittest import mock

from release_dashboard.trackers import TrackerError
from release_dashboard.trackers.pagure import PagureTracker

class TestPagureTracker:

    def test_init(self):
        """
        Check initialization requires auth token.
        """
        with pytest.raises(TrackerError):
            PagureTracker('mine')
        with pytest.raises(TrackerError):
            PagureTracker('mine', auth_token=None)
        assert PagureTracker('mine', auth_token='123')

    def test_create_issue(self):
        """
        Ensure creation of issues works as expected.
        """
        with mock.patch('libpagure.Pagure.create_issue') as _ci:
            expected_result = '100'
            _ci.return_value = {'id': expected_result}

            pg = PagureTracker('mine', auth_token='123')
            title = 'title'
            body = 'body\n\nhere'
            assert pg.create_issue(title, body) == expected_result

    def test_create_issue_with_errors(self):
        """
        Ensure creation of issues handles errors properly.
        """
        with mock.patch('libpagure.Pagure.create_issue') as _ci:
            expected_args = ['test', 'args']
            _ci.side_effect = libpagure.APIError(*expected_args)

            pg = PagureTracker('mine', auth_token='123')
            with pytest.raises(TrackerError) as err:
                pg.create_issue('title', 'body')
                assert err.args == expected_args
