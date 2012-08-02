# AGDeviceControl
# Copyright (C) 2005 The Australian National University
#
# This file is part of AGDeviceControl.
#
# AGDeviceControl is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# AGDeviceControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AGDeviceControl; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import agdevicecontrol
from agdevicecontrol.common import version
from twisted.trial import unittest

class TestVersion(unittest.TestCase):

    def test_version_components(self):
        assert hasattr(version,'major')
        assert hasattr(version,'minor')
        assert hasattr(version,'incremental')

        assert type(version.major) == type(1234)  # integer type
        assert type(version.minor) == type(1234)
        assert type(version.incremental) == type(1234)


        
    def test_version_format(self):
        assert hasattr(version,'version')

        # e.g., 0.2.1
        components = version.version.split('.') 
        assert len( components ) == 3

        major, minor, incremental = tuple( map(int,components) )
        assert major == version.major
        assert minor == version.minor
        assert incremental == version.incremental


    def test_extract_version_from_string(self):
        sample = version.version
        major, minor, incremental = version.fromString(sample)
        assert major == version.major
        assert minor == version.minor
        assert incremental == version.incremental


    def test_version_minor_difference(self):
        client_version = "0.1.0"
        server_version = "Device Server Version: 0.2.1"
        assert version.fromString(client_version) == (0,1,0)
        assert version.fromString(server_version) == (0,2,1)
        assert version.hasExpired(client_version, server_version)


    def test_version_no_difference(self):
        client_version = "0.3.7"
        server_version = "Device Server Version: 0.3.7"
        assert not version.hasExpired(client_version, server_version)


    def test_version_incremental_difference(self):
        client_version = "0.2.0"
        server_version = "Device Server Version: 0.2.1"
        self.assertRaises(version.VersionWarning, version.hasExpired, client_version, server_version)


    def test_version_as_float(self):
        assert version.toFloat("0.4.2") == 0.42


    def test_apiversion(self):
        """APIVersion doesn't include the incremental part"""
        components = version.version.split('.') 
        major, minor, incremental = tuple( map(int,components) )
        apiversion = "%d.%d" % (major, minor)
        self.assertEqual(apiversion, version.apiversion)
