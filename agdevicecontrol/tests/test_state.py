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

import agdevicecontrol
from agdevicecontrol.common.state import State
from twisted.trial import unittest

class TestState(unittest.TestCase):

    def test_empty_state(self):
        state = State()
        assert state['Power'] == None

    def test_empty_state_comparison(self):
        state1 = State()
        state2 = State()
        assert state1 == state2


    def test_nontrivial_comparison(self):
        state1 = State()
        state1['Power'] = 'On'
        state1['Position'] = (0,1)
        state1['Zoom'] = 0

        state2 = State()
        state2['Power'] = 'On'
        state2['Position'] = (0,1)
        state2['Zoom'] = 0

        state3 = State()

        assert state1 == state2
        assert state1 != state3


    def test_state_is_dictionary_like(self):
        state = State()
        state['Chicken'] = 'Bkurk'
        assert state['Chicken'] == 'Bkurk'

    def test_is_iterable(self):
        state = State()
        assert state.iterkeys() is not None

        
    def test_can_reconstruct_from_string_representation(self):

        # a non-trivial state
        state = State()
        state['Power'] = 'On'
        state['Position'] = (0,1)
        state['Zoom'] = 0

        # string representation
        r = repr(state)
        assert type(r) == type('')

        cloned_state = State(r)
        assert cloned_state == state


    def test_fromXML(self):
        s = '<state><Power value="On"/><Position value="0,0"/><Zoom value="0.0"/></state>'
        s2 = '<state><Power value="On"/><Position value="(0, 1)"/><Zoom value="0"/></state>' 

        state = State(s)
        assert state['Power'] == 'On'
        assert state['Position'] == (0,0)
        assert state['Zoom'] == 0.0


    def test_toXML(self):
        s = '<state><Power value="On"/><Position value="(0, 0)"/><Zoom value="0.0"/></state>'
        state = State()
        state['Power'] = 'On'
        state['Position'] = (0,0)
        state['Zoom'] = 0.0
        assert state.toXML() == s


    def test_tofrom_file(self):
        state = State()
        state['Power'] = 'On'
        state['Position'] = (0,1)
        state['Zoom'] = 0
        state.toFile('tmp.conf')
        
        state2 = State()
        state2.fromFile('tmp.conf')
        os.remove('tmp.conf')
        assert state == state2


    def test_from_XML2(self):
        string = '<state><Power value="On"/><PanSpeed value="0.133"/><Position value="(-27, 2)"/><Speed value="0.133"/><TiltSpeed value="0.134"/><Zoom value="0.734"/></state>'

        state = State(string)
        assert state.toXML() == string
