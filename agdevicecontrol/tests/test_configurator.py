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


configdata = """
# sample DeviceServer config file with placeholder (fictitious) devices

[authentication]
password = password123

[dev2]
device: PseudoDevice
port = 4

[dev1]
device: PseudoDevice
port = 9
"""

configdata2 = """
# sample DeviceServer config file with mixed case section name ...

[AutHenTicatIoN]
password = password123

[dev2]
device: PseudoDevice
port = 4

[dev1]
device: PseudoDevice
port = 9
"""


import os

import agdevicecontrol
from twisted.trial import unittest
from agdevicecontrol.server.configurator import IConfigurator, Configurator
from zope.interface import implements


class TestConfigurator(unittest.TestCase):

    def setUp(self):
        """Create a temporary file with above config data"""
        f = open('test_configurator.conf','w')
        f.write(configdata)
        f.close()

    def tearDown(self):
        os.remove('test_configurator.conf')


    def test_instantiate(self):
        """Instantiate an empty Configurator"""
        c = Configurator()

    def test_load_from_string(self):
        """Create a config file from string data"""
        c = Configurator()
        c.fromString(configdata)
        self.assertIn('dev1', c)

    def test_load_from_file(self):
        """Find and load a config file"""
        c = Configurator('test_configurator.conf')
        self.assertIn('dev1', c)


    def test_parsed_config_has_devices(self):
        """Parse config file correctly (sees all devices)"""
        c = Configurator('test_configurator.conf')
        self.assertEqual(len(c), 2)
        self.assertIn('dev1', c)
        self.assertIn('dev2', c)


    def test_can_create_device(self):
        """Instantiate an actual device"""
        c = Configurator('test_configurator.conf')
        k, d = c.createDevice('dev1')
        assert hash(k)
        self.assertEqual(d.getDeviceType(), 'PseudoDevice')
        self.assertEqual(d.port, 9)


    def test_no_config_file(self):
        """Generate IOError when config file missing"""

        # mustbemissing.conf must not exist for this test to function as intended
        self.failUnlessRaises(IOError, Configurator, 'mustbemissing.conf')
        

    def test_get_password(self):
        """Password gleaned correctly from config file"""
        
        c = Configurator()
        c.fromString(configdata)
        self.assertEqual(len(c), 2)
        self.assertEqual(c.getPassword(), 'password123')


    def test_no_password(self):
        """Anonymous password gleaned correctly from config file"""
        
        c = Configurator()
        self.assertEqual(c.getPassword(), '')


    def test_case_insensitivity(self):
        """Authentication section name should be case insensitive"""
        
        c = Configurator()
        c.fromString(configdata2)

        self.assertEqual(len(c), 2)
        self.assertEqual(c.getPassword(), 'password123')






#----------------------------------------------------------------------
if __name__ == "__main__":
    pass

