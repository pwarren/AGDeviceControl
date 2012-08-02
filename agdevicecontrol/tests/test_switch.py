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
from agdevicecontrol.devices.switch import Switch
from twisted.trial import unittest


class TestSwitch(unittest.TestCase):
    """Abstract device with simple power on/off ability"""


    class FooSwitch(Switch):
        pass


    def setUp(self):
        self.device = TestSwitch.FooSwitch()


    def test_device_type(self):
        """Inherited 'type' method works on subclasses"""
        self.assertEqual(self.device.getDeviceType(), "Switch")


    def test_command_list(self):
        """Public callables exposed using zope.interface mechanism"""
        known_commands = ['getCommandList', 'getDeviceType', 'getState', 'setState', 'setPowerOn', 'setPowerOff', 'getPower', 'isPowerOn', 'isPowerOff']
        known_commands.sort()
        found_commands = self.device.getCommandList()
        found_commands.sort()
        self.assertEqual(known_commands, found_commands)
