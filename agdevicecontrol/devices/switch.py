#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_switch -*-
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
from device import Device, IDevice
from agdevicecontrol.common.abstract import abstract
from zope.interface import implements, Interface


class ISwitch(IDevice):

    def setPowerOn():
        """Turn device on if necessary"""

    def setPowerOff():
        """Turn device off if necessary"""

    def getPower():
        """Returns current device state 'on' or 'off'"""

    def isPowerOn():
        """Test if device is 'on'"""
        
    def isPowerOff():
        """Test if device is 'off'"""



class Switch(Device):
    """An abstract device that can be turned on and off"""

    implements(ISwitch)

    def getDeviceType(self):
        return "Switch"
    
    def setPowerOn(self):
        abstract()

    def setPowerOff(self):
        abstract()

    def getPower(self):
        abstract()

    def isPowerOn(self):
        abstract()
        
    def isPowerOff(self):
        abstract()
