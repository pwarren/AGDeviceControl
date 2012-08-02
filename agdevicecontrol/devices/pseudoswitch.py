#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_pseudoswitch -*-
#
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
from agdevicecontrol.common.abstract import abstract
from agdevicecontrol.devices.switch import Switch, ISwitch
from zope.interface import implements


class PseudoSwitch(Switch):
    """A fictitious device for simulating an on/off switch"""

    implements(ISwitch)

    def __init__(self, *args, **kwargs):
        Switch.__init__(self, *args, **kwargs)
        self._power = False


    def setPowerOn(self):
        self._power = True

    def setPowerOff(self):
        self._power = False

    def getPower(self):
        if self._power:
            return 'On'
        else:
            return 'Off'

    def isPowerOn(self):
        return self._power
        
    def isPowerOff(self):
        return not self._power
