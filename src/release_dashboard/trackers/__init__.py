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
Tracker related integrations.
"""

from abc import ABCMeta, abstractmethod


class TrackerError(Exception):  # pragma: no cover
    """
    Base error for trackers.
    """
    pass


class Tracker(metaclass=ABCMeta):  # pragma: no cover

    @abstractmethod
    def create_issue(self, title, content, **kwargs):
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
        pass
