#!/usr/bin/env python

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
import agdevicecontrol.common.log as log
import agdevicecontrol.server.ports as ports
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from zope.interface import implements, Interface
import time


# set this to your interface IP
# FIXME: how to do this automatically?
ETH_IP = '0.0.0.0'



class IMonitor(Interface):

    def start():
        """Begin listening for heartbeats"""

    def stop():
        """Stop listening for heartbeats"""

    def newHeartbeat(callback):
        """Callback to bound function on receiving new heartbeat"""

    def lostHeartbeat(callback):
        """Callback to bound function on losing known heartbeat"""

    def redetectHeartbeat(sourceip):
        """Allow redetection of heartbeat from address, i.e., a forced drop"""



class Monitor(DatagramProtocol):
    """Responsible for tracking announcement/disappearance of heartbeats"""

    def __init__(self, address=ports.multicastgroup, port=ports.multicastport, timeout=10):

        # keyed by heartbeat ip, storing time of last heartbeat
        self.heartbeats = {}

        self.address = address
        self.port = port

        # check for timed out heartbeats every x seconds
        self.refresh = 4

        # heartbeat is "timed out" if the last known heartbeat exceeds x seconds
        self.timeout = timeout

        # callbacks
        self._newheartbeatcb = None
        self._lostheartbeatcb = None

        self.alive = False
        self.delayedcall = None



    def start(self):

        if not self.alive:
            self.huh = reactor.listenMulticast(self.port, self, interface='0.0.0.0')
            self.huh.joinGroup(self.address, interface=ETH_IP)
            self.alive = True

        # core logic to check for timed-out heartbeats
        self.delayedcall = reactor.callLater(self.refresh, self.detectTimeouts)


    def stop(self):
        self.huh.stopListening()
        self.alive = False
        if self.delayedcall:
            self.delayedcall.cancel()
            self.delayedcall = None


    def newHeartbeat(self, callback):
        self._newheartbeatcb = callback

    def lostHeartbeat(self, callback):
        self._lostheartbeatcb = callback



    def redetectHeartbeat(self, sourceip):
        """Lose track of this heartbeat allows rediscovery"""
        if sourceip in self.heartbeats:
            del self.heartbeats[sourceip]


    def datagramReceived(self, data, (sourceip, port)):
        """Twisted received a heartbeat multicast packet"""
         
        # unknown heartbeats instigate callback
        if not sourceip in self.heartbeats:
            self.heartbeats[sourceip] = time.time()
            log.write("Monitor discovered %s (%s,%d)" % (data, sourceip, port))
            if self._newheartbeatcb:
                # callback can possibly ask for redetectHeartbeat ...
                self._newheartbeatcb(sourceip, data)
        else:
            self.heartbeats[sourceip] = time.time()


    def detectTimeouts(self):
        """Detect out-of-date heartbeats

        Compare current time against time of last beat from known heartbeats.
        For expired heartbeats, we notify the bound callback.
        """

        now = time.time()
        for (ip, lastbeat) in self.heartbeats.items():
            if (now-lastbeat) > self.timeout:
                del self.heartbeats[ip]
                if self._lostheartbeatcb:
                    log.write("HeartBeat %s timed out, dropping ..." % ip)
                    self._lostheartbeatcb(ip)

        # reschedule timeout check
        self.delayedcall = reactor.callLater(self.refresh, self.detectTimeouts)


if __name__ == '__main__':

    def onNewHeartbeat(ip, data):
        m.redetectHeartbeat(ip)

    import socket
    from agdevicecontrol.common import version, copyright
    import agdevicecontrol.server.ports as ports    
    from optparse import OptionParser
    from twisted.internet import reactor
    
    print "[%s] %s" % (copyright.longversion, copyright.copyright)

    # command line parameter processing
    parser = OptionParser(usage="%prog [options]", version=copyright.version)

    parser.add_option("-g", "--group", action="store", type="string",
                      default=ports.multicastgroup,
                      dest="group",
                      help="multicast heartbeat group address")

    parser.add_option("-p", "--port", action="store", type="int",
                      default=ports.multicastport,
                      dest="port",
                      help="multicast heartbeat port")
    
    options, args = parser.parse_args()

    m = Monitor(options.group, options.port)
    m.newHeartbeat(onNewHeartbeat)

    m.start()
    reactor.run()
