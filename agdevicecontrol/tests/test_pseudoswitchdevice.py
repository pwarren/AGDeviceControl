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
from agdevicecontrol.devices.pseudoswitchdevice import PseudoSwitchDevice
from twisted.trial import unittest


class TestPseudoSwitchDevice(unittest.TestCase):
    """Compound device of pseudodevice and on/off switch"""

    def setUp(self):
        self.device = PseudoSwitchDevice(port=12)


    def test_instantiate_with_args(self):
        """Setup keyword argument appears as instance attribute"""
        assert self.device.port == 12


    def test_device_type(self):
        self.assertEqual(self.device.getDeviceType(), "Switch")


    def test_command_list(self):
        """Public callables exposed using zope.interface mechanism"""
        known_commands = ['getCommandList', 'getDeviceType', 'getState', 'setState', 'delay',
                          'getParameter', 'setParameter', 'setPowerOn', 'setPowerOff', 'getPower','raiseException',
                          'isPowerOn', 'isPowerOff' ]
        known_commands.sort()
        found_commands = self.device.getCommandList()
        found_commands.sort()
        self.assertEqual(known_commands, found_commands)

