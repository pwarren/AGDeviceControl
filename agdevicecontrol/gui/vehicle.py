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
from agdevicecontrol.common.fsm import FSM
from agdevicecontrol.gui.defaultaction import defaultaction
from agdevicecontrol.gui.device import DevicePanel
import wx.lib.evtmgr as em

#------------------------------------------------------------------------
class ClientPanel(DevicePanel):
    """Customized wx panel for controllable vehicle"""

    def __init__(self, parent, id, callback=defaultaction):

        # adjustables
        width = 600
        height = 600

        # baseclass constructor
        DevicePanel.__init__(self, parent, id, callback)

        # control window
        panelid = wx.NewId()
        self.panel = wx.Panel(self, panelid, size=(width,height), style=wx.SIMPLE_BORDER)

        # status
        self.text = wx.StaticText(self, -1, "", (width, 100), (width, -1), wx.ALIGN_CENTER)
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.text.SetFont(font)

        # event handler callbacks
        em.eventManager.Register(self.onMouseClick, wx.EVT_LEFT_DOWN, self.panel)
        em.eventManager.Register(self.onMouseRelease, wx.EVT_LEFT_UP, self.panel)
        em.eventManager.Register(self.onMouseClick, wx.EVT_RIGHT_DOWN, self.panel)
        em.eventManager.Register(self.onMouseRelease, wx.EVT_RIGHT_UP, self.panel)
        em.eventManager.Register(self.OnPaint, wx.EVT_PAINT, self.panel)
        em.eventManager.Register(self.onMove, wx.EVT_MOTION, self.panel)
        em.eventManager.Register(self.onLeavePanel, wx.EVT_LEAVE_WINDOW, self.panel)
        em.eventManager.Register(self.onEnterPanel, wx.EVT_ENTER_WINDOW, self.panel)
        wx.EVT_TIMER(self,-1, self.onTimer)


        # device context isn't available until window is actually drawn
        self.dc = None

        # rather than reacting to all mouse movements, we accumulate
        # and send updates at fixed intervals
        self.interval = 100
        self.timer = None

        # number of pixels mouse has to move in a polling period to register
        self.xsensitivity = 3
        self.ysensitivity = 3

        # set up finite state machine transitions
        self.configureFSM(self.onTransition)

        # how to do this automatically?
        self._sizer.Add(self.panel)
        self._sizer.Add(self.text)
        self._sizer.Fit(self)



    def onTransition(self, method):
        self.callback(self.device, method)
        print self.device, method
        #self.callback(method)

        # update text in GUI to match finite state machine
        self.text.SetLabel(method)


    def configureFSM(self, callback):
        """Finite state machine for mouse-movement transitions"""
        
        self.fsm = FSM('STOPPED', callback)
        self.fsm.add_transition('LMB_PRESS', 'STOPPED', None, 'MOTION_IDLING')
        self.fsm.add_transition('RMB_PRESS', 'STOPPED', None, 'TILT_IDLING')


        self.fsm.add_transition('MOUSE_STOP', 'TILT_IDLING', None, 'TILT_IDLING')
        self.fsm.add_transition('MOUSE_LEFT', 'TILT_IDLING', None, 'TILT_IDLING')
        self.fsm.add_transition('MOUSE_RIGHT', 'TILT_IDLING', None, 'TILT_IDLING')
        self.fsm.add_transition('MOUSE_UP', 'TILT_IDLING', 'tiltUp', 'TILT')
        self.fsm.add_transition('MOUSE_DOWN', 'TILT_IDLING', 'tiltDown', 'TILT')
        self.fsm.add_transition('MB_RELEASE', 'TILT_IDLING', None, 'STOPPED')

        self.fsm.add_transition('MOUSE_LEFT', 'TILT', None, 'TILT')
        self.fsm.add_transition('MOUSE_RIGHT', 'TILT', None, 'TILT')
        self.fsm.add_transition('MOUSE_STOP', 'TILT', None, 'TILT')
        self.fsm.add_transition('MOUSE_UP', 'TILT', 'tiltUp', 'TILT')
        self.fsm.add_transition('MOUSE_DOWN', 'TILT', 'tiltDown', 'TILT')
        self.fsm.add_transition('MB_RELEASE', 'TILT', None, 'STOPPED')


        self.fsm.add_transition('MOUSE_STOP', 'MOTION_IDLING', None, 'MOTION_IDLING')
        self.fsm.add_transition('MOUSE_LEFT', 'MOTION_IDLING', 'spinLeft', 'SPIN')
        self.fsm.add_transition('MOUSE_RIGHT', 'MOTION_IDLING', 'spinRight', 'SPIN')
        self.fsm.add_transition('MOUSE_UP', 'MOTION_IDLING', 'forward', 'FORWARD')
        self.fsm.add_transition('MOUSE_DOWN', 'MOTION_IDLING', 'reverse', 'REVERSE')
        self.fsm.add_transition('MB_RELEASE', 'MOTION_IDLING', 'stop', 'STOPPED')

        self.fsm.add_transition('MOUSE_LEFT', 'REVERSE', None, 'REVERSE')
        self.fsm.add_transition('MOUSE_RIGHT', 'REVERSE', None, 'REVERSE')
        self.fsm.add_transition('MOUSE_STOP', 'REVERSE', None, 'REVERSE')
        self.fsm.add_transition('MOUSE_UP', 'REVERSE', 'slowDown', 'REVERSE')
        self.fsm.add_transition('MOUSE_DOWN', 'REVERSE', 'speedUp', 'REVERSE')
        self.fsm.add_transition('MB_RELEASE', 'REVERSE', 'stop', 'STOPPED')

        self.fsm.add_transition('MOUSE_LEFT', 'SPIN', 'spinLeft', 'SPIN')
        self.fsm.add_transition('MOUSE_RIGHT', 'SPIN', 'spinRight', 'SPIN')
        self.fsm.add_transition('MOUSE_STOP', 'SPIN', None, 'SPIN')
        self.fsm.add_transition('MOUSE_UP', 'SPIN', None, 'SPIN')
        self.fsm.add_transition('MOUSE_DOWN', 'SPIN', None, 'SPIN')
        self.fsm.add_transition('MB_RELEASE', 'SPIN', 'stop', 'STOPPED')

        self.fsm.add_transition('MOUSE_STOP', 'FORWARD', None, 'FORWARD')
        self.fsm.add_transition('MOUSE_LEFT', 'FORWARD', 'turnLeft', 'TURN_LEFT')
        self.fsm.add_transition('MOUSE_RIGHT', 'FORWARD', 'turnRight', 'TURN_RIGHT')
        self.fsm.add_transition('MOUSE_UP', 'FORWARD', 'speedUp', 'SPEED_UP')
        self.fsm.add_transition('MOUSE_DOWN', 'FORWARD', 'slowDown', 'SLOW_DOWN')
        self.fsm.add_transition('MB_RELEASE', 'FORWARD', 'stop', 'STOPPED')

        self.fsm.add_transition('MOUSE_STOP', 'SPEED_UP', 'forward', 'FORWARD')
        self.fsm.add_transition('MOUSE_UP', 'SPEED_UP', 'speedUp', 'SPEED_UP')
        self.fsm.add_transition('MOUSE_DOWN', 'SPEED_UP', 'slowDown', 'SLOW_DOWN')
        self.fsm.add_transition('MOUSE_LEFT', 'SPEED_UP', 'turnLeft', 'TURN_LEFT')
        self.fsm.add_transition('MOUSE_RIGHT', 'SPEED_UP', 'turnRight', 'TURN_RIGHT')
        self.fsm.add_transition('MB_RELEASE', 'SPEED_UP', 'stop', 'STOPPED')
        
        self.fsm.add_transition('MOUSE_STOP', 'SLOW_DOWN', 'forward', 'FORWARD')
        self.fsm.add_transition('MOUSE_UP', 'SLOW_DOWN', 'speedUp', 'SPEED_UP')
        self.fsm.add_transition('MOUSE_DOWN', 'SLOW_DOWN', 'slowDown', 'SLOW_DOWN')
        self.fsm.add_transition('MOUSE_LEFT', 'SLOW_DOWN', 'forward', 'FORWARD')
        self.fsm.add_transition('MOUSE_RIGHT', 'SLOW_DOWN', 'forward', 'FORWARD')
        self.fsm.add_transition('MB_RELEASE', 'SLOW_DOWN', 'stop', 'STOPPED')
        
        self.fsm.add_transition('MOUSE_STOP', 'TURN_LEFT', 'forward', 'FORWARD')
        self.fsm.add_transition('MOUSE_LEFT', 'TURN_LEFT', 'turnLeft', 'TURN_LEFT')
        self.fsm.add_transition('MOUSE_RIGHT', 'TURN_LEFT', 'turnRight', 'TURN_RIGHT')
        self.fsm.add_transition('MOUSE_UP', 'TURN_LEFT', 'forward', 'TURN_LEFT')
        self.fsm.add_transition('MOUSE_DOWN', 'TURN_LEFT', 'forward', 'TURN_LEFT')
        self.fsm.add_transition('MB_RELEASE', 'TURN_LEFT', 'stop', 'STOPPED')

        self.fsm.add_transition('MOUSE_STOP', 'TURN_RIGHT', 'forward', 'FORWARD')
        self.fsm.add_transition('MOUSE_LEFT', 'TURN_RIGHT', 'turnLeft', 'TURN_LEFT')
        self.fsm.add_transition('MOUSE_RIGHT', 'TURN_RIGHT', 'turnRight', 'TURN_RIGHT')
        self.fsm.add_transition('MOUSE_UP', 'TURN_RIGHT', 'forward', 'TURN_RIGHT')
        self.fsm.add_transition('MOUSE_DOWN', 'TURN_RIGHT', 'forward', 'TURN_RIGHT')
        self.fsm.add_transition('MB_RELEASE', 'TURN_RIGHT', 'stop', 'STOPPED')



    def onTimer(self, event):

        # compare with previous position
        xdelta = self.position[0] - self.last_position[0]
        ydelta = self.position[1] - self.last_position[1]

        # mouse moving appreciably left
        if abs(xdelta) > self.xsensitivity:
            if xdelta < 0:
                input_symbol = "MOUSE_LEFT"
            else:
                input_symbol = "MOUSE_RIGHT"

        # mouse moving appreciably right
        elif abs(ydelta) > self.ysensitivity:
            if ydelta < 0:
                input_symbol = "MOUSE_UP"
            else:
                input_symbol = "MOUSE_DOWN"

        else:
            input_symbol = "MOUSE_STOP"

        # finite state machine action
        self.fsm.process( input_symbol )

        # needed to calculate the mouse movement delta
        self.last_position = self.position



    def OnPaint(self, event):
        """Called on startup and window refresh"""

        # drawing requires a device context, initialize if necessary
        if not self.dc:
            self.dc = wx.ClientDC(self.panel)
            self.PrepareDC(self.dc)
            self.dc.SetPen(wx.Pen("BLACK"))
            self.dc.SetBrush(wx.Brush("BLACK"))
            self.dc.SetBackground(wx.Brush("RED"))
            self.dc.Clear()
        

    def onMouseClick(self, event):
        """Mouse Button Pressed"""

        # sanity check, old timer should have been nixed prior to new left click ...
        if self.timer:
            return

        # current mouse coords are our new "zero" position
        self.position = event.GetPosition()
        self.last_position = self.position

        # state machine action
        if event.LeftDown():
            self.fsm.process( "LMB_PRESS" )
        elif event.RightDown():
            self.fsm.process( "RMB_PRESS" )

        # green for go
        self.dc.SetBackground(wx.Brush("GREEN"))
        self.dc.Clear()

        # callback in milliseconds
        self.timer = wx.Timer(self)
        self.timer.Start(self.interval)


    def onEnterPanel(self, event):
        """Mouse moved into control area"""
        self.dc.SetBackground(wx.Brush("YELLOW"))
        self.dc.Clear()


    def onLeavePanel(self, event):
        """Mouse moved outside window border"""

        # stop moving if cursor leaves control area ...
        self.removeTimer()

        # red for stopped
        self.dc.SetBackground(wx.Brush("RED"))
        self.dc.Clear()


    def onMouseRelease(self, event):
        """Mouse Button Released"""
        self.removeTimer()

        # yellow for yield
        self.dc.SetBackground(wx.Brush("YELLOW"))
        self.dc.Clear()


    def removeTimer( self ):
        if self.timer:
            self.timer.Stop()
            del self.timer
            self.timer = None

            # state machine action
            self.fsm.process( "MB_RELEASE" )


    def onMove(self, event):
        """Capture mouse movement events"""

        # only if left mouse is down ...
        if self.timer:
            self.position = event.GetPosition()
