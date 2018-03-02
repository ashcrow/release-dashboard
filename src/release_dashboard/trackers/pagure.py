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
Pagure tracker integrator.
"""

import os

from libpagure import Pagure, APIError

from release_dashboard.trackers import Tracker, TrackerError


class PagureTracker(Tracker):
    """
    Implements the integration for Pagure.

    Example::

       pg = PagureTracker('atomic-wg', auth_token='secret')
       issue_id = pg.create_issue('subject', 'the body\nof the ticket')
    """

    def __init__(self, project, auth_token=os.getenv('PAGURE_TOKEN')):
        """
        Creates an instance of the Pagure tracker integration.

        :param repo: The name of the project to work with.
        :type repo: str
        :param auth_token: Authentication token. Default: env:PAGURE_TOKEN.
        :type auth_token: str
        :raises: release_dashboard.trackers.TrackerError
        """
        if auth_token is None:
            raise TrackerError('No valid token found')
        self.pg = Pagure(pagure_token=auth_token, pagure_repository=project)

    def create_issue(self, title, body):
        """
        Creates an issue in an external tracker.

        :param title: The title of the issue.
        :type title: str
        :param body: The main body/content of the issue.
        :type body: str
        :param kwargs: Any other keyword arguments specific to the tracker.
        :type kwargs: dict
        :returns: The identifier of the new issue
        :rtype: str
        :raises: release_dashboard.trackers.TrackerError
        """
        try:
            result = self.pg.create_issue(title=title, content=body)
            return str(result['id'])
        except APIError as err:
            raise TrackerError(*err.args)
