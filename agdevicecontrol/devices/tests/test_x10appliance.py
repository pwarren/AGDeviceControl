
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


from py.test import raises
import py
import time

from x10appliance import X10Appliance

class TestX10Appliance:
    """test Driver for x10 appliance modules"""

    disabled = 0

    def test_instantiation_with_args(self):
        a = X10Appliance(port=0, house='A', number=1)
        assert a is not None

    def test_On(self):
        a = X10Appliance(port=0,house='A',number=1)
        assert a.setPower('On') is None
        time.sleep(1)

    def test_Off(self):
        a = X10Appliance(port=0,house='A',number=1)
        assert a.setPower('Off') is None


    def test_instantiation_with_args2(self):
        a = X10Appliance(port=0, house='B', number=2)
        assert a is not None

    def test_HouseB(self):
        a = X10Appliance(port=0, house='B', number=2)
        assert a.setPower('On') is None
