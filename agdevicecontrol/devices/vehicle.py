
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


from device import Device
from agdevicecontrol.common.abstract import abstract

class Vehicle(Device):
    """Vehicle Abstract Class"""

    def __init__(self, *args, **kwargs):
        Device.__init__(self, *args, **kwargs)


    def showType(self):
        return "Vehicle"


    # Concrete instances of Vehicle *must* implement these methods 

    def stop(self):
        abstract()
    
    def turnLeft(self):
        abstract()
    
    def turnRight(self):
        abstract()
    
    def speedUp(self):
        abstract()

    def slowDown(self):
        abstract()

    def tiltUp(self):
        abstract()

    def tiltDown(self):
        abstract()

    def spinLeft(self):
        abstract()

    def spinRight(self):
        abstract()

    def spinStop(self):
        abstract()

    def forward(self):
        abstract()

    def reverse(self):
        abstract()


class VehicleException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

