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
from agdevicecontrol.devices.device import Device, IDevice
from twisted.trial import unittest

class TestDevice(unittest.TestCase):

    class FakeDevice(Device):
        def __init__(self, *args, **kwargs):
            Device.__init__(self,*args,**kwargs)

    def setUp(self):
        self.device = TestDevice.FakeDevice(port=7)


    def test_implements_interface(self):
        assert IDevice.providedBy(self.device)

    def test_device_type(self):
        assert self.device.getDeviceType() == 'Device'


    def test_command_list(self):
        known_commands = ['getCommandList', 'getDeviceType', 'getState', 'setState']
        known_commands.sort()
        found_commands = self.device.getCommandList()
        found_commands.sort()
        self.assertEqual(known_commands, found_commands)


    def test_keyword_arguments_autoset(self):
        assert self.device.port == 7


    def test_dictionary_arguments_autoset(self):
        g = TestDevice.FakeDevice( {'port': 11} )
        assert g.port == 11


    def test_has_exceptions(self):
        assert 'UnknownCommandWarning' in dir(self.device)
        assert 'BusyWarning' in dir(self.device)
        assert 'RangeWarning' in dir(self.device)
