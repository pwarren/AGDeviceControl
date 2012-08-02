#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_pseudoswitchdevice -*-
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
from agdevicecontrol.devices.pseudodevice import PseudoDevice, IPseudoDevice
from agdevicecontrol.devices.pseudoswitch import PseudoSwitch, ISwitch


class IPseudoSwitchDevice(ISwitch, IPseudoDevice):
    """Combined pseudodevice power off/on switch interface"""


class PseudoSwitchDevice(PseudoSwitch, PseudoDevice):
    """Compound fictitious device used for testing framework without actual hardware"""

    implements(IPseudoSwitchDevice)

    # device type is inherited from Switch, probably safer to
    # make this explicit in subclasses, viz.
    #
    # def getDeviceType(self):
    #    return "Switch"
    #