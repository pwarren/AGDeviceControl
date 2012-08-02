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

from agdevicecontrol.common import resource
from agdevicecontrol.gui.switch import ClientPanel as SwitchPanel
from agdevicecontrol.gui.parameterswitch import ParameterSwitch
from agdevicecontrol.gui.bitmapbutton import BitmapButton
from agdevicecontrol.gui.defaultaction import defaultaction
from agdevicecontrol.gui.device import DevicePanel


#------------------------------------------------------------------------
class ClientPanel(DevicePanel):
    
    def __init__(self, parent, id, bridge=None):

        # baseclass constructor
        DevicePanel.__init__(self, parent, id, bridge)

        # images in agdevicecontrol/clients/images directory, need fully qualified paths
        images = resource.globdict("agdevicecontrol.gui", subdir="images", filter='*.png')

        # movement buttons numbered like telephone dialpad, 1-9 from bottom left
        bitmaps_normal = [ images['img%dn.png' % (i+1)] for i in range(9) ]
        bitmaps_pressed = [ images['img%dp.png' % (i+1)] for i in range(9) ]

        # actions on button press
        self.onpress_actions = { 1:'PanLeftTiltDown', 2:'TiltDown', 3:'PanRightTiltDown',
                                 4:'PanLeft', 5:'MoveHome', 6:'PanRight',
                                 7:'PanLeftTiltUp', 8:'TiltUp', 9:'PanRightTiltUp' }


        # populate a 3x3 grid for movement buttons
        grid_sizer = wx.GridSizer(3,3,0,0)
        for mid in [7,8,9,4,5,6,1,2,3]:
            button = BitmapButton(self, mid, self.movePress, self.moveRelease,
                                  bitmaps_normal[mid-1], bitmaps_pressed[mid-1])  # images start at 1
            grid_sizer.Add(button, 0, wx.EXPAND)
        grid_sizer.Fit(self)


        # (continuous|quantised) movement checkbox.  Default is quantised, press
        # movement button and camera moves fixed (hopefully zoom dependent) amount
        self.continuous = ParameterSwitch(self, -1, 'Continuous Movement', callback=self.continuousMove)
        self.continuous_move = False

        # zoom buttons
        self.zoom = wx.BoxSizer(wx.HORIZONTAL)
        zoominbutton = BitmapButton(self, id, self.zoomInPress, self.zoomRelease,
                                    images['zoomin0.png'], images['zoomin1.png'])
        self.zoom.Add(zoominbutton)
        zoomoutbutton = BitmapButton(self, id, self.zoomOutPress, self.zoomRelease,
                                    images['zoomout0.png'], images['zoomout1.png'])
        self.zoom.Add(zoomoutbutton)

        
        # power toggle
        self.power = wx.RadioBox(self, -1, '', wx.DefaultPosition, wx.DefaultSize,
                             ['Off','On'], 2, wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        em.eventManager.Register(self.setPower, wx.EVT_RADIOBOX, self.power)



        # labels
        label_movement = wx.StaticText(self, -1, 'Movement:', style=wx.ALIGN_RIGHT)
        label_zoom = wx.StaticText(self, -1, 'Zoom:', style=wx.ALIGN_RIGHT)
        label_power = wx.StaticText(self, -1, 'Power:', style=wx.ALIGN_RIGHT)


        # variable size n x 2 grid for overall alignment
        flexgridsizer = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=25)
        flexgridsizer.AddMany( [label_movement, grid_sizer,
                                (0,0), self.continuous,
                                label_zoom, self.zoom,
                                label_power, self.power] )

        # how to do this automatically?
        self._sizer.Add(flexgridsizer)
        self._sizer.Fit(self)



    def zoomInPress(self, event):
        if self.continuous_move:
            self.deviceExecute('ZoomInStart')
        else:
            self.deviceExecute('ZoomIn')

    def zoomOutPress(self, event):
        if self.continuous_move:
            self.deviceExecute('ZoomOutStart')
        else:
            self.deviceExecute('ZoomOut')

    def zoomRelease(self, event):
        if self.continuous_move:
            self.deviceExecute('ZoomStop')

    def movePress(self, id):
        """Called by BitmapButton class on mouse press

        id is telephone keypad-like number 1-9.  For
        continuous movement, commands are postfixed with
        'Start'.
        """

        # not for MoveHome
        if id != 5 and self.continuous_move:
            self.deviceExecute( self.onpress_actions[id]+'Start' )
        else:
            print "DEBUG: ", self.onpress_actions[id]
            self.deviceExecute( self.onpress_actions[id] )


    def moveRelease(self, id):
        if id != 5:  # not needed for MoveHome
            if self.continuous_move:
                self.deviceExecute( 'PanTiltStop' )

    
    def continuousMove(self, bool):
        self.continuous_move = bool


    def setPower(self, event):
        self.deviceExecute("setPower%s" % self.power.GetStringSelection() )
        event.Skip()



    def updateDevice(self):
        """Refresh the camera panel"""

        # only camera state is power On/Off ... query device and update gui via callback
        self.deviceExecute("isPowerOn", callback=self._updatePowerSwitch)


    def _updatePowerSwitch(self, returnvalue):
        print "Camera.getPower returns ", returnvalue

        if returnvalue:
            self.power.SetStringSelection('On')
        else:
            self.power.SetStringSelection('Off')

