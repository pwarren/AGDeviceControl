#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_device -*-
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
from agdevicecontrol.common.state import State
from agdevicecontrol.common.abstract import abstract
from zope.interface import implements, providedBy, Interface, classProvides
import types


class IDeviceFactory(Interface):

    def __call__(*args, **kwargs):
        """Create a Device object with attributes populated from dictionary/keyword args"""


class IDevice(Interface):

    def getState():
        """Serialize the current state of the device"""

    def setState(state):
        """Restore a device's saved settings from serialized state"""

    def getDeviceType():
        """Device's type is its classname"""

    def getCommandList():
        """List of (public) callables of subclassed device"""



#class DeviceError(Exception):
from twisted.spread import pb
class DeviceError(pb.Error):
    pass



class Device:
    """Abstract baseclass for all devices"""

    implements(IDevice)
    classProvides(IDeviceFactory)


    def __init__(self, *args, **kwargs):

        # hack ...
        for arg in args:
            if type(arg) == types.DictType:
                kwargs = arg
                break

        # bind attributes to device
        for key in kwargs:
            setattr( self, key, kwargs[key] )

        # ini-style config file loses type info, know port should be an integer ...
        try:
            self.port = int(self.port)
        except AttributeError:
            pass

      
    def getState(self):
        abstract()

    def setState(self,state):
        abstract()
        
        
    def getCommandList(self):
        commands = []
        for interface in providedBy(self):
            for cmd in list(interface):
                if cmd not in commands:
                    commands.append(cmd)
        return commands


    def getDeviceType(self):
        return "Device"


    class BusyWarning(DeviceError):
        pass

    class UnknownCommandWarning(DeviceError):
        pass

    class RangeWarning(DeviceError):
        pass

