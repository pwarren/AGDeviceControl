#/usr/bin/env python

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


import wx
from agdevicecontrol.devices.device import DeviceError


class DeviceNotebook(wx.Notebook):

    def __init__(self, parent, id, bridge=None):

        # superclass constructor
        wx.Notebook.__init__(self, parent, id, size=(21,21), style=wx.NB_TOP)

        # persistent references
        self.parent = parent  # clientframe?
        self.bridge = bridge
        self.panels = []

        # devicepanels keyed by devicetype 
        self.devicetypes = {}



    def addDevice(self, device, devicetype):
        # existing devicetype, just add to listbox ...
        if devicetype in self.devicetypes:
            self.devicetypes[devicetype].addDevice( device )
            self.devicetypes[devicetype].setDevice( device )

        else:
            # need a new notebook tab and appropriate devicetype panel

            # this should really be done automagically ...
            if devicetype == "Camera":
                from agdevicecontrol.gui import camera
                panel = camera.ClientPanel
            elif devicetype == "Vehicle":
                from agdevicecontrol.gui import vehicle
                panel = vehicle.ClientPanel
            elif devicetype == "Projector":
                from agdevicecontrol.gui import projector
                panel = projector.ClientPanel
            elif devicetype == "Switch":
                from agdevicecontrol.gui import switch
                panel = switch.ClientPanel
            elif devicetype == "PseudoDevice":
                from agdevicecontrol.gui import pseudodevice
                panel = pseudodevice.ClientPanel
            else:
                raise DeviceError, "Unknown device type %s" % devicetype
            new_panel = panel(self, -1, self.bridge)
            new_panel.addDevice( device )
            #new_panel.setDevice( device )

            # so we know what to remove later
            self.panels.append( devicetype )
            
            self.devicetypes[devicetype] = new_panel
            self.AddPage(new_panel, devicetype)


    def removeDevice(self, device, devicetype):
            self.devicetypes[devicetype].removeDevice( device )


    def removeDevicePage(self, panel):
        for devicetype, dpanel in self.devicetypes.items():
            if panel == dpanel:
                self.DeletePage(self.panels.index(devicetype))
                self.panels.remove(devicetype)
                del self.devicetypes[devicetype]
                break
            
            
