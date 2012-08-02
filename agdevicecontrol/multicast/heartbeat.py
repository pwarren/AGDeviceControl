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
import agdevicecontrol.server.ports as ports
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from zope.interface import implements, Interface
from time import time


class IHeartbeat(Interface):

    def setMessage(msg):
        """Generic user-defined message to broadcast"""

    def setTransmitInterval(interval):
        """Send heartbeats at 'interval' seconds"""

    def start():
        """Begin sending heartbeats"""

    def stop():
        """Stop sending heartbeats"""

    def setDebugMode(flag):
        """Set debug mode True/False"""



class Heartbeat(DatagramProtocol):
    """Send UDP heartbeat packets at defined frequency"""

    def __init__(self, address=ports.multicastgroup, port=ports.multicastport, message=""):
        self.interval = 1
        self.address = address
        self.port = port
        self.message = message
        self.alive = False
        self.delayedcall = None
        self.debug = False


    def setMessage(self, msg):
        self.message = msg

    def startProtocol(self):
        pass

    def start(self, *args):

        # don't really understand this, why 'listenMulticast' for a sender?  Is this
        # really just a group join command to the router?  (DEE)
        if not self.alive:
            self.huh = reactor.listenMulticast(0, self, interface='0.0.0.0')
            self.huh.setTTL(127)
            self.alive = True

        self.delayedcall = reactor.callLater(self.interval, self.sendDatagram)


    def stop(self):
        self.huh.stopListening()
        self.alive = False
        if self.delayedcall:
            self.delayedcall.cancel()
            self.delayedcall = None


    def sendDatagram(self):
        if self.debug:
            print "Sending message : %s" %(self.message)
        
        self.transport.write(self.message, (self.address, self.port))
        if self.alive:
            self.delayedcall = reactor.callLater(self.interval, self.sendDatagram)


    def setTransmitInterval(self, interval):
        self.interval = interval


    def setDebugMode(self, flag):
        self.debug = flag



if __name__ == '__main__':
    
    import agdevicecontrol
    from agdevicecontrol.common import version, copyright
    import agdevicecontrol.server.ports as ports
    from optparse import OptionParser
    import socket
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

    parser.add_option("-m", "--message", action="store", type="string",
                      default="%s's heartbeat" % (socket.gethostname()),
                      dest="msg",
                      metavar="MSG",
                      help="Message to put through the heartbeat")

    parser.add_option('-d', "--debug", action="store_true",
                      dest="debug",
                      help="Show debug information")


    options, args = parser.parse_args()

    hb = Heartbeat(options.group, options.port, options.msg)

    if options.debug:
        hb.setDebugMode(True)
    
    hb.start()
    reactor.run()
