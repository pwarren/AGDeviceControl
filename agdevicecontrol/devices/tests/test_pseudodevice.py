
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


from pseudodevice import PseudoDevice
import device

class TestPseudoDevice:
    """Fictitious device used for testing framework without actual hardware"""

    disabled = 0

    def test_instantiate_with_args(self):
        d = PseudoDevice(port=4)
        assert d.port == 4


    def test_device_type(self):
        d = PseudoDevice(port=4)
        assert d.showType() == "PseudoDevice"
        

    def test_exports_known_commands(self):
        d = PseudoDevice(port=4)
        for cmd in d.showCommandList():
            assert cmd in command_list
            command_list.remove(cmd)
        assert len(command_list) == 0


    def test_delay(self):
        d = PseudoDevice(port=4)
        py.test.raises(PseudoDevice.BusyWarning, "d.delay()")
