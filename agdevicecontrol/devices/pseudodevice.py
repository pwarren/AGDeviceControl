#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_pseudodevice -*-
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
from zope.interface import implements, Interface
from agdevicecontrol.devices.device import Device, IDevice, DeviceError
import time


class IPseudoDevice(Interface):
    """Public interface to the PseudoDevice"""

    def delay(seconds):
        """Sleep for seconds"""

    def getParameter():
        """Retrieve stored value"""

    def setParameter(value):
        """Store an arbitrary Python value"""
        
    def raiseException():
        """Raise a known exception"""



class PseudoDevice(Device):
    """Fictitious device used for testing framework without actual hardware"""

    implements(IDevice,IPseudoDevice)

    def __init__(self, *args, **kwargs):
        Device.__init__(self, *args, **kwargs)
        self._parameter = 0

    def getDeviceType(self):
        return "PseudoDevice"

    def getParameter(self):
        return self._parameter

    def setParameter(self, value):
        self._parameter = value

    def delay(self, seconds):
        time.sleep(seconds)

    def raiseException(self):
        raise DeviceError
