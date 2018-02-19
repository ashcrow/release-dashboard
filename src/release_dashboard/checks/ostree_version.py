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


import os
import re
import tempfile

import guestfs
import requests


class OstreeVersionSniffer:
    """
    Class for retrieving and inspecting ostree data from an image.

    Example::

       with OstreeVersionSniffer('Fedora-Atomic-27-20180216.0') as o:
           print(o.get_ostree_version())

    Example::

       o = OstreeVersionSniffer('Fedora-Atomic-27-20180216.0')
       print(o.get_ostree_version())
       o.clean_up()
    """

    def __init__(self, version):
        """
        Initialize a new instance of OstreeVersionSniffer.

        :param version: The version to inspect.
        :type version: str
        """
        self._image_path = None
        self._version = version

    def __enter__(self):  # pragma: no cover
        """
        Used for context management.
        """
        self.download_image(self._version)
        return self

    def download_image(self, version):
        """
        Downloads a specific cloud image to inspect.

        :param version: The version of the image to download.
        :type version: str
        """
        url = ("https://kojipkgs.fedoraproject.org/compose/twoweek/"
               "{}/compose/CloudImages/x86_64/images/{}.x86_64.qcow2".format(
                   version, version))
        _, self._image_path = tempfile.mkstemp()
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise Exception(
                'Non 200 result getting install.img: {}'.format(r.status_code))
        with open(self._image_path, 'wb') as fobj:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    fobj.write(chunk)

    def get_ostree_version(self):
        """
        Gets the ostree version from a downloaded image.

        :returns: The found ostree version
        :rtype: str
        """
        try:
            g = guestfs.GuestFS(python_return_dict=True)
            g.add_drive_opts(self._image_path, format="qcow2", readonly=0)
            g.launch()
            g.mount('/dev/atomicos/root', '/')
            dir = g.ls('/ostree/deploy/fedora-atomic/deploy/')[0]
            data = g.cat(
                '/ostree/deploy/fedora-atomic/deploy/'
                '{}/usr/lib/os.release.d/os-release-fedora'.format(dir))
            print(type(data), data)
            version = re.findall("OSTREE_VERSION=(.*)", data)[0]
            g.shutdown()
            return version
        except Exception as ex:
            raise Exception(
                'Unable to read ostree version: {}: {}'.format(type(ex), ex))

    def clean_up(self):
        """
        Removes the downloaded image if it exists.
        """
        if self._image_path:
            os.unlink(self._image_path)

    def __exit__(self, type, value, traceback):  # pragma: no cover
        """
        Do cleanup on context management exit.
        """
        self.clean_up()
