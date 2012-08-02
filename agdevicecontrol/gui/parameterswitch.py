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


class ParameterSwitch(wx.CheckBox):

    def __init__(self, parent, id, label, callback=defaultaction):
        wx.CheckBox.__init__(self, parent, -1, label, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        self.callback = callback
        em.eventManager.Register(self.set, wx.EVT_CHECKBOX, self)


    def set(self, event):
        self.callback( event.IsChecked() )
