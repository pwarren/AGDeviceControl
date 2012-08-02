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
from agdevicecontrol.multicast.monitor import Monitor
from agdevicecontrol.multicast.heartbeat import Heartbeat
import agdevicecontrol.server.ports as ports
from twisted.trial import unittest
from twisted.internet import reactor
import socket


class TestHeartbeat(unittest.TestCase):

    def setUpClass(self):
        self.localip = socket.gethostbyname(socket.gethostname())
    
    def tearDownClass(self):
        pass


    def setUp(self):
        self.failure = None

        # choose port that we likely aren't using ...
        self.port = ports.multicastport + 1001
        self.heartbeat = Heartbeat(port=self.port)
        self.monitor = Monitor(port=self.port, timeout=5)
        self.monitor.newHeartbeat(self._onNewHeartbeat)



    def tearDown(self):
        self.heartbeat.stop()
        self.monitor.stop()


    def succeeded(self, *args):
        """Allow reactor iteration loop in test proper to exit and pass test"""
        self.done = True
        self.timeout.cancel()  # safety timeout no longer necessary
        self.lastargs = args  # make persistent for later checks


    def failed(self, reason):
        """Allow reactor iteration loop in test proper to exit and fail test"""
        self.done = True
        self.failure = reason
        self.lastargs = None



    def _onNewHeartbeat(self, host, data):
        if host == self.localip:
            self.succeeded()
        else:
            print "WARNING: Received a heartbeat from %s with data '%s'" % (host,data)


    def _onLostHeartbeat(self, host):
        if host == self.localip:
            self.succeeded()
        else:
            print "WARNING: Received a dropped heartbeat from %s" % host



    def test_heartbeat(self):

        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "Timed out listening for heartbeat on default address/port... failing")

        self.monitor.start()
        self.heartbeat.start()
        
        # idle until code above triggers succeeded or timeout causes failure
        self.done = False
        while not self.done:
            reactor.iterate(0.1)
       
        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)


        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "Timed out waiting for expected dropped heartbeat ... failing")

        # stop heartbeat, expect notification ...
        self.monitor.lostHeartbeat(self._onLostHeartbeat)

        # idle until code above triggers succeeded or timeout causes failure
        self.done = False

        self.heartbeat.stop()
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)
