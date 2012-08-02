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
import agdevicecontrol
from agdevicecontrol.common import copyright, version
from agdevicecontrol.common.preset import Preset
from agdevicecontrol.common.state import State
import agdevicecontrol.common.log as log


class MenuBar(wx.MenuBar):

    _about = """
    'AGDeviceControl Client' is a wxPython-based GUI client
    used to control physical devices residing on an
    AGDeviceControl server.

    More information can be found at 
    http://agcentral.org/downloads/agdevicecontrol

%s""" % copyright.copyright

    def __init__(self, parent):

        # superclass constructor
        wx.MenuBar.__init__(self)

        # persistent references
        self.parent = parent

        # menu ids
        ID_EXIT = wx.NewId()
        ID_ABOUT = wx.NewId()
        ID_REFRESH = wx.NewId()
        ID_LOAD = wx.NewId()
        ID_SAVE = wx.NewId()
        
        fmenu = wx.Menu()
        # fmenu.Append(ID_LOAD, '&Load', 'Load a Preset file')
        # fmenu.Append(ID_SAVE, '&Save', 'Save settings as Preset')
        # fmenu.AppendSeparator()
        fmenu.Append(ID_EXIT, 'E&xit', 'Quit the Program')

        hmenu = wx.Menu()
        hmenu.Append(ID_ABOUT, '&About', 'Information about the program')

        # add top-level menus to menu bar
        self.Append(fmenu, '&File')
        self.Append(hmenu, '&Help')

        # menu events bound to parent (the frame)
        #wx.EVT_MENU(self.parent, ID_LOAD, self.onLoad)
        #wx.EVT_MENU(self.parent, ID_SAVE, self.onSave)
        wx.EVT_MENU(self.parent, ID_ABOUT, self.onAbout)
        wx.EVT_MENU(self.parent, ID_EXIT, self.parent.onExit)


    def onAbout(self, event):
        log.write("About dialog activated")
        d = wx.MessageDialog(self, MenuBar._about, "AGDeviceControl client %s" % version.version, wx.OK)
        d.ShowModal()
        log.write("About dialog closed")
        d.Destroy()


##    def onLoad(self, event):
##        log.write("Load dialog activated")
##        self.dirname=os.getcwd() 
##        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.preset", wx.OPEN) 
##        if dlg.ShowModal() == wx.ID_OK: 
##            self.filename = dlg.GetFilename() 
##            self.dirname = dlg.GetDirectory() 
##            f = os.path.join(self.dirname, self.filename)
##            preset = Preset(f)
##            for name in preset:
##                self.connector.sendCommand(name,'setState',preset[name])
##        dlg.Destroy() 


##    def onSave(self, event):
##        log.write("Save dialog activated")
##        self.dirname = os.getcwd() 
##        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.preset", wx.SAVE) 
##        if dlg.ShowModal() == wx.ID_OK:
##            self.filename = dlg.GetFilename()
##            self.dirname = dlg.GetDirectory()
##            f = os.path.join(self.dirname, self.filename)
##            preset = Preset()
##            for device in self.connector.getDeviceList():
##                tmp_string = self.connector.sendCommand(device,'getState')
##                tmp_state = State(tmp_string)
##                preset[device] = tmp_state
##            preset.toFile(f)

