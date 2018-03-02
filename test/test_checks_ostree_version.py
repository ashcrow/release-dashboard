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
Tests for ostre_version.
"""

import os.path
import tempfile

import pytest
import requests

from io import BytesIO
from unittest import mock


# Skip this test if guestfs can not be used
try:
    import guestfs
except:
    import sys
    sys.stderr.write('\n\n!!! Unable to import guestfs. '
          'Coverage will likely not be able to meet the minimum !!!\n\n')
    pytest.importorskip("guestfsa")

from release_dashboard.checks import ostree_version

OS_RELEASE = """\
NAME=Fedora
VERSION="27.16 (Twenty Seven)"
ID=fedora
VERSION_ID=27
PRETTY_NAME="Fedora 27.16 (Twenty Seven)"
ANSI_COLOR="0;34"
CPE_NAME="cpe:/o:fedoraproject:fedora:27"
HOME_URL="https://fedoraproject.org/"
OSTREE_VERSION=27.16
"""


class TestAtomicOstreeVersionSniffer:

    def test_init(self):
        """
        Check initialization requires one parameter.
        """
        # Fail eith no input
        with pytest.raises(TypeError):
            ostree_version.OstreeVersionSniffer()

        version = '1.2.3'
        ovs = ostree_version.OstreeVersionSniffer(version)
        assert ovs._version == version

    def test_clean_up(self):
        """
        Ensure clean_up removes files when a file exists.
        """
        ovs = ostree_version.OstreeVersionSniffer('1.2.3')
        # Nothing should be removed
        assert ovs._image_path == None
        ovs.clean_up()
        _, ovs._image_path = tempfile.mkstemp()
        assert os.path.isfile(ovs._image_path) is True
        ovs.clean_up()
        assert os.path.isfile(ovs._image_path) is False

    def test_download_image(self):
        """
        Verify downloading of images writes out the image to a local file
        with the expected information.
        """
        version = '1.2.3'
        out_file = './test_data'
        data = 'sentry data'
        try:
            with mock.patch('requests.get') as _get:
                with mock.patch('tempfile.mkstemp') as _mkstemp:
                    resp = requests.Response()
                    resp.status_code = 200
                    resp.raw = BytesIO(bytes(data, 'utf8'))
                    _get.return_value = resp
                    # Override the temp file creation so we can clean up
                    _mkstemp.return_value = ('', out_file)
                    ovs = ostree_version.OstreeVersionSniffer(version)
                    ovs.download_image(version)
            # Verify the content is what we expect
            with open(out_file, 'r') as fobj:
                assert fobj.read() == data
        finally:
            try:
                os.unlink(out_file)
            except FileNotFoundError:
                pass

    def test_get_ostree_version(self):
        """
        Verify that ostree_version can find the version and return it.
        """
        version = '1.2.3'
        fake_hash = 'HAAAAASH'
        with mock.patch('guestfs.GuestFS') as _gfs:
            _gfs().ls.return_value = [fake_hash]

            def verify_path(path):
                expected = (
                    '/ostree/deploy/fedora-atomic/deploy/' +
                    fake_hash + '/usr/lib/os.release.d/os-release-fedora')
                assert path == expected
                return OS_RELEASE

            # Verify the path looked it as what we expect
            _gfs().cat.side_effect = verify_path
            ovs = ostree_version.OstreeVersionSniffer(version)
            # Ensure the right version was found and returned
            assert ovs.get_ostree_version() == '27.16'
