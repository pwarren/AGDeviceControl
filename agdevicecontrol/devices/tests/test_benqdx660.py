
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
import time

from dx660 import DX660

class TestBenqDX660:

    disabled = 0

    #def test_instantiation(self):
    #    a = DX660()
        
        
    def test_instantiation_with_kwargs(self):
        a = DX660(port=1)
        assert a.port == 1

    def test_instantiation_with_dictargs(self):
        a = DX660( {'port':1} )
        assert a.port == 1

    def test_On(self):
        a = DX660(port=1)
        assert a.setPower('On') is None

    def test_Off(self):
        a = DX660(port=1)
        time.sleep(5)
        assert a.setPower('Off') is None
