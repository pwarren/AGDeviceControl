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
from agdevicecontrol.devices.pseudoswitch import PseudoSwitch
from twisted.trial import unittest


class TestPseudoSwitch(unittest.TestCase):

    def setUp(self):
        self.device = PseudoSwitch()


    def test_device_type(self):
        self.assertEqual(self.device.getDeviceType(), "Switch")


    def test_power_commands(self):
        """Silly tests exercising PseudoSwitch logic"""

        self.assertEqual( self.device.getPower(), 'Off')

        self.device.setPowerOff()
        self.assertEqual( self.device.getPower(), 'Off')
        self.assertEqual( self.device.isPowerOn(), False)
        self.assertEqual( self.device.isPowerOff(), True)

        self.device.setPowerOn()
        self.assertEqual( self.device.getPower(), 'On')
        self.assertEqual( self.device.isPowerOn(), True)
        self.assertEqual( self.device.isPowerOff(), False)
        
