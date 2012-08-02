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
from agdevicecontrol.gui.menubar import MenuBar
from agdevicecontrol.gui.devicenotebook import DeviceNotebook
from agdevicecontrol.clients.bridge import WXBridge
import agdevicecontrol.common.log as log
from twisted.internet import reactor


class ClientFrame(WXBridge):

    def __init__(self, parent, id, title):

        # baseclass constructor
        WXBridge.__init__( self, parent, id, title)

        # configure menu bar (also sets the local onExit callback)
        self.SetMenuBar( MenuBar(self) )
        self.CreateStatusBar()

        # notebook with one tab per device type, e.g., 'Cameras', 'Projectors'
        log.write('Creating TabbedNotebook')
        self.notebook = DeviceNotebook(self, -1, self)

        self.Layout()

        # super-duper important ....
        reactor.interleave(wx.CallAfter)




    def onExit(self, event):
        print "debug1" 
        log.write('Exiting application')

        # let twisted reactor shut down first ...
        reactor.addSystemEventTrigger('after', 'shutdown', self.Close, True)
        reactor.stop()
