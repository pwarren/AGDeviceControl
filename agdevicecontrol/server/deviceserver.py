#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_deviceserver -*-
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
from twisted.internet import reactor, threads
from twisted.internet import defer
from twisted.internet.defer import Deferred
from zope.interface import implements, Interface

from agdevicecontrol.server.configurator import Configurator
from agdevicecontrol.server.devicequeue import DeviceQueue
from agdevicecontrol.common import version
from agdevicecontrol.common.container import Container




class IDeviceServer(Interface):

    def loadConfig(config):
        """Parse the ini-style config file and instantiate the listed devices"""

    def deviceExecute(device, command, params=None):
        """Queue and execute command(params) method for named device"""

    def getPassword():
        """Retrieve plain-text server password"""

    def getDeviceList():
        """List of all available devices (in Containers)"""

    def getDeviceType(device):
        """String type of named device"""

    def getCommandList(device):
        """Command list for named device"""

    def getDeviceMap():
        """Dictionary of devices (in Containers) keyed by type"""



#-----------------------------------------------------------------------

class PBDeviceServer(pb.Avatar):
    """Exposes remote interface via persistent broker.

    Important to note that this class is instantiated for each connection.
    It should stay lightweight with all possibly persistent state residing in
    the DeviceServer
    """

    def __init__(self, ds):
        self.ds = ds


    def perspective_getVersion(self):
        print "getVersion() = %s" % version.version
        return defer.succeed(version.version)


    def perspective_getDeviceList(self):
        value = self.ds.getDeviceList()
        print "getDeviceList() = %s" % value
        return defer.succeed(value)


    def perspective_getDeviceType(self, device):
        value = self.ds.getDeviceType(device)
        print "getDeviceType(%s) = %s" % (device, value)
        return defer.succeed(value)


    def perspective_getCommandList(self, device):
        value = self.ds.getCommandList(device)
        print "getCommandList(%s) = %s" % (device, value)
        return defer.succeed(value)


    def perspective_getDeviceMap(self):
        value = self.ds.getDeviceMap()
        print "getDeviceMap() = %s" % value
        return defer.succeed(value)


    def perspective_deviceExecute(self, device, command, params=None):
        print "submitted deviceExecute(%s, %s, %s)" % (device, command, params)
        return self.ds.deviceExecute(device, command, params)



#-----------------------------------------------------------------------
class DeviceServer:

    implements(IDeviceServer)

    def __init__(self, config):

        self.config = config
        if not isinstance(config,Configurator):
            self.loadConfig(config)

	#dictionary of devices, keyed by a Container with relevant info in it.
        self.devices = {}

        # each device has a command queue
        self.queues = {}

	# dictionary of device containers, keyed by type.
        self._devicemap = {}

        for device in self.config.sections():
	    con = Container()

	    key, instance = self.config.createDevice(device)
	    
	    con.name = key
	    con.type = instance.getDeviceType()

            try:
                self._devicemap[instance.getDeviceType()].append(con)
            except KeyError:
                self._devicemap[instance.getDeviceType()] = [con]
            self.devices[con] = instance
            self.queues[con] = DeviceQueue()



    def loadConfig(self, config):
        self.config = Configurator(config)


    def getPassword(self):
        return self.config.getPassword()


    def deviceExecute(self, device, command, param=None):
        if device in self.getDeviceList():
            if command in self.getCommandList(device):
                # bound method of desired device
                device_method = getattr(self.devices[device], command)

                # convenient reference
                queue = self.queues[device]

                # add to device queue
                d = queue.submit(device_method, param)

                return d



    def getDeviceList(self):
        return self.devices.keys()


    def getDeviceType(self, device):
        return self.devices[device].getDeviceType()


    def getCommandList(self, device):
        return self.devices[device].getCommandList()


    def getDeviceMap(self):
        return self._devicemap


