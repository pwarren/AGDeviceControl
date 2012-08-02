#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_bridge -*-
#
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


from agdevicecontrol.clients.connector import Connector
from agdevicecontrol.multicast.transport import decode
import agdevicecontrol.common.log as log
from twisted.internet import reactor

import wx
from wx.lib.newevent import NewEvent
from wx import PostEvent
import wx.lib.evtmgr as em


class EventRegistry:

    def __init__(self):
        self.events = {}
        self.factorydict = {}


    def createEventFactory(self, name):
        factory, identifier = NewEvent()
        self.factorydict[name] = {'factory': factory, 'identifier': identifier}


    def createEvent(self, name):
        return self.factorydict[name]['factory'](fun = lambda: attr(*args, **kwargs))



class TwistedBridge:

    def __init__(self, monitor):

        # heartbeat
        self.monitor = monitor

        # create wx events with which Twisted can signal the GUI
        self.eventregistry = EventRegistry()
        self.eventregistry.createEventFactory('addDevice')
        self.eventregistry.createEventFactory('removeDevice')
        self.eventregistry.createEventFactory('commandResult')

        self.deviceconnectormap = {}
        self.devicetypemap = {}



    def setWXBridge(self, other):
        self.wxbridge = other


    def newHeartbeat(self, sourceip, data):
        try:
            name, host, port, passwd = decode(data)
        except ValueError:
            return
        self.addConnector(host, port, passwd)


    def addConnector(self, host, port, passwd):
        """Attempt connection to Aggregator, notification via callback"""
        log.write( "TwistedBridge attempting Connector(%s,%d)" % (host,port) )
        connector = Connector(host, port)
        connector.connect(self._addConnectorSuccess, errback=self._addConnectorFailure, password=passwd)


    def _addConnectorSuccess(self, connector):
        log.write('TwistedBridge Connector(%s,%d) connected successfully' % (connector.host, connector.port) )

        connector.notifyOnDisconnect(self._onConnectionDropped)
        connector.getDeviceMap(self._getDeviceMapSuccess)


    def _addConnectorFailure(self, failure, connector):
        log.write( "TwistedBridge Connector(%s,%d) failed to connect, redetectHeartbeat" % (connector.host, connector.port) )
        self.monitor.redetectHeartbeat(connector.host)


    def _getDeviceMapSuccess(self, devicemap, connector):
        log.write( "TwistedBridge Connector(%s,%s) received devicemap: %s" % (connector.host, connector.port, devicemap) )
        for devicetype,devicelist in devicemap.items():
            for device in devicelist:
                log.write("\tPosting WXEvent adding  '%s' (%s)" % (device,devicetype))
                
                event = self.eventregistry.createEvent('addDevice')
                event.devicetype = devicetype
                event.device = device
                PostEvent(self.wxbridge, event)
                self.devicetypemap[device] = devicetype
                self.deviceconnectormap[device] = connector



    def lostHeartbeat(self, host):
        pass
    

    def _onConnectionDropped(self, droppedconnector):

        for device,connector in self.deviceconnectormap.items():
            if connector == droppedconnector:

                event = self.eventregistry.createEvent('removeDevice')
                event.device = device
                event.devicetype = self.devicetypemap[device]
                PostEvent(self.wxbridge, event)
                
                del self.deviceconnectormap[device]
                del self.devicetypemap[device]



    def deviceExecute(self, device, command, parameters):
        self.deviceconnectormap[device].deviceExecute(device, command, parameters, \
                                                      callback=self._deviceExecuteSuccess)


    def _deviceExecuteSuccess(self, returnvalue, connector, device, command, parameters):

        event = self.eventregistry.createEvent('commandResult')
        event.returnvalue = returnvalue
        event.device = device
        event.command = command
        event.parameters = parameters
        PostEvent(self.wxbridge, event)



class WXBridge(wx.Frame):

    def __init__(self, parent, id, title):

        # baseclass constructor
        wx.Frame.__init__( self, parent, id, title, size = (430,460),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE )

        self.callables = {}



    def setTwistedBridge(self, other):
        self.twistedbridge = other

        er = self.twistedbridge.eventregistry
        for name in er.factorydict.keys():
            event = er.factorydict[name]
            em.eventManager.Register(getattr(self,name), event['identifier'], self)

        other.setWXBridge(self)


    def deviceExecute(self, device, command, parameters, callback=None):
        try:
            self.callables[(device,command,parameters)].append(callback)
        except KeyError:
            self.callables[(device,command,parameters)] = [callback]

        self.twistedbridge.deviceExecute(device, command, parameters)


    def addDevice(self, event):
        log.write( "WXBridge.addDevice: %s %s" % (event.device, event.devicetype) )
        self.notebook.addDevice(event.device, event.devicetype)


    def removeDevice(self, event):
        log.write("WXBridge.removeDevice: %s" % event.device)
        self.notebook.removeDevice(event.device, event.devicetype)


    def commandResult(self, event):
        log.write( "WXBridge: %s.%s(%s) = %s" % (event.device, event.command, event.parameters, event.returnvalue) )

        cb = self.callables[ (event.device,event.command,event.parameters) ].pop(0)
        if cb:
            cb(event.returnvalue)
