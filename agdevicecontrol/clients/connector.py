#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_connector -*-
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

import agdevicecontrol
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import credentials, error
from zope.interface import implements, Interface
import agdevicecontrol.server.ports as ports
from agdevicecontrol.common import version


class IConnector(Interface):

    def connect(callback, errback=None, password=None):
        """On successful connection to remote server, callback with self"""

    def close():
        """Terminate connection with cleanup"""

    def notifyOnDisconnect(callback):
        """Client wants notification on disconnection"""


    def getDeviceList(callback, errback=None):
        """Callback with list of available devices on remote server"""

    def getDeviceType(device, callback, errback=None):
        """Callback with type string of named device"""

    def getCommandList(device, callback, errback=None):
        """Callback with list of available commands on named device"""

    def deviceExecute(device, command, parameters=None, callback=None, errback=None):
        """Execute remote command, callback with results if any"""



class ConnectorError(Exception):
    pass


class Connector:
    """Moderates connection between client and Device|Aggregator"""

    implements(IConnector)


    def __init__(self, host, port=ports.deviceserver):
        self.host = host
        self.port = port
        self.pbroot = None
        self.devicelist = None
        self.devicetype = {}
        self.devicemap = {}
        self.cmdlists = {}
        self.connected = None
        self.callback = None
        self.ondisconnectcb = None


    def close(self):
        """Terminate connection, not yet implemented"""


    def connect(self, callback, errback=None, password=''):
        """Attempt connection to remote PB Server"""
        factory = pb.PBClientFactory()
        reactor.connectTCP(self.host, self.port, factory)
        d = factory.login(credentials.UsernamePassword(version.apiversion,password))
        d.addCallback(self._onConnectSuccess)
        d.addErrback(self._onConnectFailure)

        d.addCallback(callback)
        if errback:
            d.addErrback(errback, self)


    def _onConnectSuccess(self, root):
        """Twisted successfully got a perspective on remote root object"""
        self.pbroot = root
        self.connected = True

        # FIXME: untested code
        self.pbroot.notifyOnDisconnect(self._onDisconnect)
        
        return self


    def _onConnectFailure(self, failure):
        """Twisted failed to get a perspective on remote root object"""
        self.connected = False
        failure.trap(error.UnauthorizedLogin)
        return failure



    def notifyOnDisconnect(self, callback):
        self.ondisconnectcb = callback

    def _onDisconnect(self, _):
        """Connection lost"""
        self.connected = False
        if self.ondisconnectcb:
            self.ondisconnectcb(self)


    def getDeviceList(self, callback, errback=None):
        if self.connected:
            d = self.pbroot.callRemote("getDeviceList")
            d.addCallback(callback, self)
            if errback:
                d.addErrback(errback)


    def getDeviceType(self, device, callback, errback=None):
        if self.connected:
            d = self.pbroot.callRemote("getDeviceType", device)
            d.addCallback(callback, self, device)
            if errback:
                d.addErrback(errback)
            

    def getCommandList(self, device, callback, errback=None):
        if self.connected:
            d = self.pbroot.callRemote("getCommandList", device)
            d.addCallback(callback, self, device)
            if errback:
                d.addErrback(errback)


    def deviceExecute(self, device, command, parameters=None, callback=None, errback=None):
        if self.connected:
            d = self.pbroot.callRemote("deviceExecute", device, command, parameters)
            d.addCallback(callback, self, device, command, parameters)
            if errback:
                d.addErrback(errback)


    def getDeviceMap(self, callback, errback=None):
        if self.connected:
            d = self.pbroot.callRemote("getDeviceMap")
            d.addCallback(callback, self)
            if errback:
                d.addErrback(errback)

