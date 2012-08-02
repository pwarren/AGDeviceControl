#!/usr/bin/env python
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


# supports wx and twisted together ...
import agdevicecontrol
from twisted.internet import threadedselectreactor
threadedselectreactor.install()

import wx
from optparse import OptionParser
import sys
import socket

from agdevicecontrol.multicast.monitor import Monitor
from agdevicecontrol.multicast.heartbeat import Heartbeat
from agdevicecontrol.multicast.transport import encode
from agdevicecontrol.clients.bridge import TwistedBridge, WXBridge
from agdevicecontrol.server.aggregator import Aggregator, PBAggregator, create_portal
from agdevicecontrol.gui.clientframe import ClientFrame
from agdevicecontrol.gui.menubar import MenuBar
from agdevicecontrol.gui.devicenotebook import DeviceNotebook
from agdevicecontrol.common import version, copyright
from agdevicecontrol.gui.defaultaction import defaultaction
import agdevicecontrol.server.ports as ports


from twisted.application import service
from twisted.internet import reactor
from twisted.python import threadable
from twisted.application import internet
from twisted.spread import pb


# set this to your interface IP
# FIXME: how to do this automatically?
global ETH_IP
ETH_IP = '0.0.0.0'


def run():
		
     # local heartbeat and Aggregator
     if options.aggregator:

          aggregator = Aggregator(options.agconfig)
          portal = create_portal(aggregator)
          
          heartbeat = Heartbeat(address=options.group, port=options.port)
          localip = socket.gethostbyname(socket.gethostname())
          heartbeat.setMessage(encode(options.id, localip, options.agport, aggregator.getPassword()))
          
          reactor.listenTCP(options.agport, pb.PBServerFactory(portal))
          aggregator.notifyOnMapped(heartbeat.start)

     # heartbeat monitor
     monitor = Monitor(address=options.group, port=options.port)

     # wx-twisted communication bridge (mediator)
     global twistedbridge
     twistedbridge = TwistedBridge(monitor)

     # monitor reports to the bridge via callbacks
     monitor.newHeartbeat(twistedbridge.newHeartbeat)
     monitor.lostHeartbeat(twistedbridge.lostHeartbeat)

     monitor.start()

     app = MyApp(redirect=False)
     app.MainLoop()


class MyApp(wx.App):
     
     def OnInit(self):
          global twistedbridge
          frame= ClientFrame(None, -1, "AGDeviceControl Client")
          frame.setTwistedBridge(twistedbridge)
          frame.Show(True)
          self.SetTopWindow(frame)
          return True


#--------------------------------------------------------------------------
if __name__ == '__main__':
	
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


    parser.add_option('-a', "--aggregator", action="store_true",
                      dest="aggregator",
                      help="Run an Aggregator on the local machine")

    parser.add_option('-f', "--aggregator-config", action="store",
                      type="string",
                      dest="agconfig",
                      default="./aggregator.conf",
                      help="config file for local aggregator")

    parser.add_option("-t", "--aggregator-port", action="store", type="int",
                      default=ports.aggregator,
                      dest="agport",
                      help="aggregator to listen for control commands port")

    parser.add_option("-i", "--id", action="store", type="string",
                      default=socket.gethostname(),
                      dest="id",
                      metavar="ID",
                      help="identifying ID for multicast heartbeat")


    parser.add_option("-l", "--log", action="store", type="string",
                      dest="logfile",
                      metavar="FILE",
                      help="record log data to FILE")

    parser.add_option('-d', "--debug", action="store_true",
                      dest="debug",
                      help="Show debug information")

    options, args = parser.parse_args()


    run()
    
