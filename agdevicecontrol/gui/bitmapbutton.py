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


class BitmapButton(wx.StaticBitmap):
    """Custom bitmapped 'button' with different pressed/released images"""
    
    def __init__(self, parent, id, onpress, onrelease, imgnormal, imgpressed):
        
        self.parent = parent
        self.id = id

        wx.InitAllImageHandlers()

        # wxPython 2.4 on Linux/GTK doesn't support bitmap masking
        self.normal = wx.Bitmap(imgnormal, wx.BITMAP_TYPE_PNG)
        try:
            mask = wx.Mask(self.normal, wx.WHITE)
            self.normal.SetMask(mask)
        except:
            pass
        self.height = self.normal.GetHeight()
        self.width = self.normal.GetWidth()
        self.size = (self.width, self.height)

        self.active = wx.Bitmap(imgpressed, wx.BITMAP_TYPE_PNG)
        try:
            mask = wx.Mask(self.active, wx.WHITE)
            self.active.SetMask(mask)
        except:
            pass

        # baseclass constructor
        wx.StaticBitmap.__init__(self, parent, -1, self.normal, self.size)

        # event handlers
        em.eventManager.Register(self.onPress, wx.EVT_LEFT_DOWN, self)
        em.eventManager.Register(self.onRelease, wx.EVT_LEFT_UP, self)
        em.eventManager.Register(self.onRelease, wx.EVT_LEAVE_WINDOW, self)

        self.onpress = onpress
        self.onrelease = onrelease

        # inital button state is unpressed
        self.pressed = False


    def onPress(self, event):
        self.pressed = True
        self.SetBitmap(self.active)
        if callable(self.onpress):
            self.onpress(self.id)


    def onRelease(self, event):
        if self.pressed:  # sanity check
            self.SetBitmap(self.normal)
            if callable(self.onrelease):
                self.onrelease(self.id)
            self.pressed = False
