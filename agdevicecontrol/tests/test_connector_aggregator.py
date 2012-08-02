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

import os, os.path
import types

import agdevicecontrol
from agdevicecontrol.server.deviceserver import DeviceServer
import agdevicecontrol.server.ports as ports
from agdevicecontrol.devices.device import DeviceError
from agdevicecontrol.clients.connector import Connector
from agdevicecontrol.common import version

from twisted.trial import unittest
from twisted.internet import reactor, error
from twisted.test.test_process import SignalMixin
from agdevicecontrol.tests.subprocessprotocol import SubProcessProtocol



aggregator_config_contents = """
# aggregator with no devices ...
"""



class TestConnector(SignalMixin, unittest.TestCase):

    def setUpClass(self):
        """Start an Aggregator in a child process to test against"""

        # aggregator startup script directory
        bindir = os.path.join(agdevicecontrol.path, 'server')

        # keep track of temporary files for deletion in tearDown
        self.tempfiles = []

        # create a temporary aggregator config file
        filename = 'test_aggregator.conf'
        fqfilename = bindir + os.sep + filename
        f = open(fqfilename,'w')
        f.write(aggregator_config_contents)
        f.close()
        self.tempfiles.append(fqfilename)

        # start aggregator as a child process
        self.process = SubProcessProtocol()
        self.process.waitOnStartUp(['aggregator.py', filename, '-n', '--test'], path = bindir)
        if self.process.running is False:
            raise unittest.SkipTest, "Aggregator didn't start correctly, skipping tests"
        import time
        time.sleep(1)


    def tearDownClass(self):
        """Stop the Aggregator running in a child process"""
        print "*** tearDownClass: ", self.process.done
        self.process.waitOnShutDown()

        # clean-up temporary config files
        for f in self.tempfiles:
            os.remove(f)



    def setUp(self):
        """Per test initalization"""
        self.done = False
        self.failure = None

    def tearDown(self):
        """Per test cleanup code"""
        if self.connector:
            self.connector.close()


    def succeeded(self, *args):
        """Allow reactor iteration loop in test proper to exit and pass test"""
        self.done = True
        self.timeout.cancel()  # safety timeout no longer necessary
        self.lastargs = args  # make persistent for later checks


    def failed(self, reason, unknown):
        """Allow reactor iteration loop in test proper to exit and fail test"""
        self.done = True
        self.failure = reason
        self.lastargs = None


    def test_simple_connect(self):
        """Obtain perspective on Aggregator"""

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "attempt to connect to Aggregator timed out ... failing")

        self.connector = Connector('localhost', port=8789)
        self.connector.connect(callback=self.succeeded, errback=self.failed, password='bkurk')
        
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)

        connector = self.lastargs[0]
        assert connector == self.connector

        # paranoia check
        assert self.connector.connected is True

        

    
    if False:
        test_simple_connect.skip = True


