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

import jinja2

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

    def create_templatized_issue(self, title, template_name, context):
        """
        Creates an issue in an external tracker based on a template.

        :param title: The title of the issue.
        :type title: str
        :param body: Name of internal template or full path.
        :type template_name: str
        :param context: Context to pass to the template.
        :type context: dict
        :returns: The identifier of the new issue
        :rtype: str
        :raises: release_dashboard.trackers.TrackerError
        """
        tpl = None
        if template_name.startswith('/'):
            try:
                with open(template_name, 'r') as template_fobj:
                    tpl = jinja2.Template(template_fobj.read())
            except Exception as err:
                raise TrackerError(err.__class__.__name__, *err.args)
        else:
            try:
                env = jinja2.Environment(
                    loader=jinja2.PackageLoader(
                        'release_dashboard', 'templates'),
                    autoescape=jinja2.select_autoescape(['html']))
                tpl = env.get_template(template_name)
            except jinja2.exceptions.TemplateError as err:
                raise TypeError(err.__class__.__name__, *err.args)

        content = tpl.render(**context)
        return self.create_issue(title, content)
