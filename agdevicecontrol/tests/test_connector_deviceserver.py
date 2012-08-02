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
from agdevicecontrol.devices.device import DeviceError
from agdevicecontrol.clients.connector import Connector
from agdevicecontrol.common import version

from twisted.trial import unittest
from twisted.internet import reactor, error
from twisted.test.test_process import SignalMixin
from agdevicecontrol.tests.subprocessprotocol import SubProcessProtocol

import sys
from twisted.python import log
log.startLogging(sys.stdout)

deviceserver_config_contents = """
# deviceserver configuration file created by test_connector.py

[Authentication]
password: bkurk

[Device1]
device: PseudoDevice
port: 1

[Device2]
device: PseudoDevice
port: 0
"""



class TestConnector(SignalMixin, unittest.TestCase):

    def setUpClass(self):
        """Start a DeviceServer in a child process to test against"""

        # deviceserver startup script directory
        bindir = os.path.join(agdevicecontrol.path, 'bin')

        # keep track of temporary files for deletion in tearDown
        self.tempfiles = []

        # create a temporary deviceserver config file
        filename = 'test_deviceserver.conf'
        fqfilename = bindir + os.sep + filename
        f = open(fqfilename,'w')
        f.write(deviceserver_config_contents)
        f.close()
        self.tempfiles.append(fqfilename)

        # start deviceserver as a child process
        self.process = SubProcessProtocol()
        self.process.waitOnStartUp(['server.py', filename, '-n'], path = bindir)
        if self.process.running is False:
            raise unittest.SkipTest, "DeviceServer didn't start correctly, skipping tests"


    def tearDownClass(self):
        """Stop the DeviceServer running in a child process"""
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


    def failed(self, reason):
        """Allow reactor iteration loop in test proper to exit and fail test"""
        self.done = True
        self.failure = reason
        self.lastargs = None



    def test_unauthorized_connect(self):
        """Should fail to connect (unauthorized)"""

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "attempt to connect to DeviceServer timed out ... failing")

        self.connector = Connector('localhost')
        self.connector.connect(callback=self.failed, errback=self.succeeded)
        
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)

        # paranoia check
        assert self.connector.connected is False




    def test_simple_connect(self):
        """Obtain perspective on DeviceServer"""

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "attempt to connect to DeviceServer timed out ... failing")

        self.connector = Connector('localhost')
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



    def test_connect_to_nonexistent_server(self):
        """Attempt to connect to known non-existent deviceserver"""

        # safety timeout
        self.timeout = reactor.callLater(15, self.failed, "attempt to connect to DeviceServer timed out ... failing")

        self.connector = Connector('localhost', port=9999)  # assumption
        self.connector.connect(callback=self.failed, errback=self.succeeded, password='nomatter')
         
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)
            print "self.connector.connected: ", self.connector.connected

        # paranoia check
        assert self.connector.connected is False
 
        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)



    def test_connect_and_execute(self):
        """Connect and issue simple command"""

        # wait for slow, single CPU machine to get twisted going in another thread.
        import time
        time.sleep(1)
        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to connect to DeviceServer timed out ... failing")

        self.connector = Connector('localhost')
        self.connector.connect(callback=self.succeeded, errback=self.failed, password='bkurk')
        
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)


	self.timeout = reactor.callLater(5, self.failed, "Attempt to get devicelist timed out ... failing")

	# get a device key for use in next step
	self.done = False
	self.connector.getDeviceList(self.succeeded, errback=self.failed)

	while not self.done:
	    reactor.iterate(0.1)

	if self.failure:
	    self.fail(self.failure)

	print
	print "DEBUG:"
	print self.lastargs[0][0]
	device = self.lastargs[0][0]
	    

        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to getParameter timed out ... failing")

        self.connector.deviceExecute(device, 'getParameter', callback=self.succeeded, errback=self.failed)

        # idle until code above triggers succeeded or timeout causes failure
        self.done = False
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)

        # expected return values
        value, connector, device, command, params = self.lastargs
        assert type(value) == types.IntType
        assert connector == self.connector
        assert device == 'Device1'
        assert command == 'getParameter'
        assert params == None


    def test_connect_and_get_devicemap(self):
        """Connect and retrieve devicemap"""

        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to connect to DeviceServer timed out ... failing")

        self.connector = Connector('localhost')
        self.connector.connect(callback=self.succeeded, errback=self.failed, password='bkurk')
         
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)

        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to getDeviceMap timed out ... failing")

        self.connector.getDeviceMap(callback=self.succeeded, errback=self.failed)

        # idle until code above triggers succeeded or timeout causes failure
        self.done = False
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)

        # expected return values
        devmap = self.lastargs[0]
        assert len(devmap) == 1
        assert 'PseudoDevice' in devmap
        assert len(devmap['PseudoDevice']) == 2
        assert 'Device1' in devmap['PseudoDevice']
        assert 'Device2' in devmap['PseudoDevice']



    def test_connect_and_raise_exception(self):
        """Connect and raise pseudodevice error"""

        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to connect to DeviceServer timed out ... failing")

        self.connector = Connector('localhost')
        self.connector.connect(callback=self.succeeded, errback=self.failed, password='bkurk')
         
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)


        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to raise remote exception timed out ... failing")
        self.done = False

        self.connector.deviceExecute('Device1', 'raiseException', callback=self.failed, errback=self.succeeded)

        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.fail(self.failure)

        # expecting returnvalue of exception
        # should still be connected ...

        # safety timeout
        self.timeout = reactor.callLater(5, self.failed, "attempt to getDeviceMap timed out ... failing")

        self.connector.getDeviceMap(callback=self.succeeded, errback=self.failed)

        # idle until code above triggers succeeded or timeout causes failure
        self.done = False
        while not self.done:
            reactor.iterate(0.1)

        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            assert connector.connected is False
            self.fail(self.failure)

        # expected return values
        devmap = self.lastargs[0]
        self.assertEqual(self.connector.connected, True)
        

    
    if False:
        test_unauthorized_connect.skip = True
        test_simple_connect.skip = True
        test_connect_to_nonexistent_server.skip = True
        test_connect_and_execute.skip = True
        test_connect_and_get_devicemap.skip = True
        test_connect_and_raise_exception.skip = True

