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
import wx.lib.evtmgr as em
from agdevicecontrol.common.abstract import abstract


class DevicePanel(wx.Panel):
    """Base class for all devices exposing a wx interface

    DevicePanel places a listbox of accessible devices at
    the top of the panel, derived classes flesh this out
    with custom controls relevent to their devicetype"""
    
    def __init__(self, parent, id, bridge):

        # superclass constructor
        wx.Panel.__init__(self, parent, id)

        self.bridge = bridge
        self.parent = parent
        
	self._devicelist = wx.ListBox(self, -1, (0,0), (250,150), [], wx.LB_SINGLE)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self._devicelist)
        self.SetSizer(self._sizer)
        self.SetAutoLayout(1)

        # listbox selection will set this
        self.device = None

        em.eventManager.Register(self.onSelection, wx.EVT_LISTBOX, self._devicelist)



    def onSelection(self, event):
        self.device = self._devicelist.GetClientData(event.GetSelection())
        print "DevicePanel.onSelection: ", self.device
        self.updateDevice()


    def setDevice(self, device):
        if device in self._devices:
            self.device = device

            
    def addDevice(self, device):
	
	self._devicelist.Append(device.name, clientData=device)
	self.device = device
	self.updateDevice()
	
        
    def removeDevice(self, device):

        self._devicelist.Delete(self._devicelist.FindString(device.name))
	
        if len(self) == 0:
            # parent.removeDevicePage ???
            # or send an event ???
            print "Notebook page empty ..."
            self.parent.removeDevicePage(self)
            

    def __len__(self):
        return self._devicelist.GetCount()


    def updateDevice(self):
        """Must be implemented by derived class.  Called on selection
        of new device telling GUI to refresh based on device state"""
        abstract()


    def deviceExecute(self, command, parameters=None, callback=None):
        if self.bridge:
            self.bridge.deviceExecute(self.device, command, parameters, callback)
