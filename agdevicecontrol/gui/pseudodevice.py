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

from agdevicecontrol.gui.device import DevicePanel


#------------------------------------------------------------------------
class ClientPanel(DevicePanel):
    
    def __init__(self, parent, id, bridge=None):

        # baseclass constructor
        DevicePanel.__init__(self, parent, id, bridge)

        self.parameter = wx.TextCtrl(self, -1, "0", size=(125, -1))
        #em.eventManager.Register(self.setParameter, wx.EVT_TEXT, self.parameter)

        self.delay = wx.TextCtrl(self, -1, "1", size=(125, -1))

        self.b = wx.Button(self, -1, 'Go!', size=(125, -1))
        em.eventManager.Register(self.setParameter, wx.EVT_BUTTON, self.b)

        # labels
        label_parameter = wx.StaticText(self, -1, 'Parameter:', style=wx.ALIGN_RIGHT)
        label_delay = wx.StaticText(self, -1, 'Delay:', style=wx.ALIGN_RIGHT)

        # variable size n x 2 grid for overall alignment
        flexgridsizer = wx.FlexGridSizer(rows=3, cols=3, vgap=10, hgap=25)
        flexgridsizer.AddMany( [label_parameter, self.parameter, self.b,
                                label_delay, self.delay] )

        # how to do this automatically?
        self._sizer.Add(flexgridsizer)
        self._sizer.Fit(self)


    def setParameter(self, event):
        self.deviceExecute("setParameter", self.parameter.GetValue(), callback=self._setParameterSuccess)
        event.Skip()


    def _setParameterSuccess(self, returnvalue):
        print "PseudoDevice.setParameter returns ", returnvalue


    def updateDevice(self):
        """Refresh the pseudodevice panel"""
        self.deviceExecute("getParameter", callback=self._getParameterSuccess)


    def _getParameterSuccess(self, returnvalue):
        print "PseudoDevice.getParameter returns ", returnvalue
        self.parameter.SetValue(str(returnvalue))
        
