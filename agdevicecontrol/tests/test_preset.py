
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

import os
from agdevicecontrol.common.state import State
from agdevicecontrol.common.preset import Preset



class TestPreset:
    """Tests for the preset object

    Assumes that 'preset1.preset' defines a PseudoDevice preset to
    integer = 1, tuple = (10,20), float = 3.4145
    """
    
    disabled = 0

    def test_instantiate(self):
        p = Preset()
        assert p is not None


    def test_fail_on_missing(self):
        # to succeed, 'missing.preset' must *not* exist
        py.test.raises(IOError, Preset, 'missing.preset')


    def test_preset_1(self):
        p1 = Preset('data' + os.sep + 'sample.preset')
        assert p1.getNames() is not None


    def test_preset_2(self):
        """Make sure that a preset is a dictionary of states"""
        p1 = Preset('data' + os.sep + 'sample.preset')
        s1 = State()
        for name in p1:
            assert type(p1[name]) == type(s1)


    def test_to_file(self):
        p1 = Preset()
        s1 = State()
        s1['Power'] = 'On'
        s1['Position'] = (1,0)
        p1['cam1'] = s1
        p1.toFile('tmp.preset')
        p2 = Preset('tmp.preset')
        os.remove('tmp.preset')

        assert p1 == p2


        
