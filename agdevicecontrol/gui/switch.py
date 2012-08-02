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

from agdevicecontrol.gui.defaultaction import defaultaction
from agdevicecontrol.gui.device import DevicePanel


class ClientPanel(DevicePanel):
    
    def __init__(self, parent, id, callback=defaultaction):

        # baseclass constructor
        DevicePanel.__init__(self, parent, id, callback)

        self.label = wx.StaticText(self, -1, 'Power:', style=wx.ALIGN_RIGHT)
        self.toggle = wx.RadioBox(self, -1, '', wx.DefaultPosition, wx.DefaultSize,
                             ['Off','On'], 2, wx.RA_SPECIFY_COLS | wx.NO_BORDER)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.label)
        sizer.Add(self.toggle)

        em.eventManager.Register(self.set, wx.EVT_RADIOBOX, self.toggle)


        # how to do this automatically?
        self._sizer.Add(sizer)
        self._sizer.Fit(self)



    def set(self, event):
        self.callback(self.device,  "Power" + self.toggle.GetStringSelection() )
        event.Skip()

