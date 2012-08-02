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


import os
import random
import types

import agdevicecontrol
from agdevicecontrol.server.aggregator import Aggregator
from agdevicecontrol.server.configurator import Configurator

from twisted.internet import defer, reactor
from twisted.trial import unittest
from twisted.spread import pb
import agdevicecontrol.server.ports as ports
from twisted.test.test_process import SignalMixin
from agdevicecontrol.tests.subprocessprotocol import SubProcessProtocol


configdata = """
# sample Aggregator.conf

[DeviceServer1]
host: localhost
port: %s
password: bkurk

""" % ports.deviceserver



class TestAggregator(SignalMixin, unittest.TestCase):

    def setUpClass(self):
        """Start a DeviceServer in a child process to test against"""

        self.deviceserverprocess = SubProcessProtocol()
        self.deviceserverprocess.waitOnStartUp( ['server.py', 'deviceserver.conf', '-n'], \
                                                path=os.path.join(agdevicecontrol.path,'bin') )

        if self.deviceserverprocess.running is False:
            raise unittest.SkipTest, "DeviceServer didn't start correctly, skipping tests"

        #wait for slow single CPU buildbots to catch up
        import time
        time.sleep(1)

        # use the config above
        conf = Configurator()
        conf.fromString(configdata)

        # can be set by timeout
        self.failure = False


        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "Aggregator failed to connect to all deviceservers ... failing")
        
        self.aggregator = Aggregator(conf)
        self.done = False
        while not self.done:
            print "Waiting for aggregator to connect to deviceservers"
            reactor.iterate(0.1)
            if self.aggregator.connected:
                self.succeeded()

        if self.failure:
            raise unittest.SkipTest, "Aggregator didn't connect to all deviceservers ... skipping tests"



        # FIXME: we really should handle missing and newly appearing deviceservers.

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "Aggregator failed to map all deviceservers ... failing")

        self.aggregator.notifyOnMapped(self.succeeded)

        self.done = False
        while not self.done:
            print "Waiting for aggregator to map deviceservers"
            reactor.iterate(0.1)


        if self.failure:
            raise unittest.SkipTest, "Aggregator didn't start correctly, skipping tests"



    def tearDownClass(self):
        """Stop the DeviceServer running in a child process"""
        print "*** tearDownClass: ", self.deviceserverprocess.done
        self.deviceserverprocess.waitOnShutDown()


    def succeeded(self, *args):
        """Allow reactor iteration loop in test proper to exit and pass test"""
        self.done = True
	if self.timeout is not None:
	    self.timeout.cancel()  # safety timeout no longer necessary
        self.timeout = None
        self.lastargs = args  # make persistent for later checks


    def failed(self, reason):
        """Allow reactor iteration loop in test proper to exit and fail test"""
        self.done = True
        self.failure = reason
        self.timeout.cancel()  # safety timeout no longer necessary
        self.timeout = None

    def setUp(self):
        """I'm called at the very beginning of each test"""
        self.done = False
        self.failure = None
        self.timeout = None


    def tearDown(self):
        """I'm called at the end of each test"""
        if self.timeout:
            self.timeout.cancel()


    def timedOut(self):
        """I'm called when the safety timer expires indicating test probably won't complete"""

        print "timedOut callback, test did not complete"
        self.failed("Safety timeout callback ... test did not complete")
        reactor.crash()


        

    #---------- tests proper ------------------------------------

    def test_handled_configurator(self):
        """Aggregator instantiated with a configurator rather than .conf filename"""
        assert 'DeviceServer1' in self.aggregator.config


    def test_password(self):
        """Aggregator should have random password"""

        assert type(self.aggregator.getPassword()) == type("")

        # ensure a second instance has differing password ...
        conf = Configurator()
        conf.fromString('')
        other = Aggregator(conf)
        assert other.getPassword() != self.aggregator.getPassword()



    def test_devicelist_as_deferred(self):
        """Return aggregated device list"""

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "retrieving devicelist timed out ... failing")

        d = self.aggregator.getDeviceList()
        assert isinstance(d, defer.Deferred)
        d.addCallback(self.succeeded)
        
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
            reactor.iterate(0.1)
        
        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.failed(self.failure)

        devicelist = self.lastargs[0]
        assert len(devicelist) == 2
        assert 'Device1' in devicelist
        assert 'Device2' in devicelist



    def test_devicemap_as_deferred(self):
        """Return aggregated device map"""

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "retrieving devicemap timed out ... failing")

        d = self.aggregator.getDeviceMap()
        assert isinstance(d, defer.Deferred)

        # caution: as this deferred is ready-to-go, the callback is called *immediately*
        d.addCallback(self.succeeded)
        # i.e., self.succeeded has now been called
        
        # idle until code above triggers succeeded or timeout causes failure
        while not self.done:
             reactor.iterate(0.1)
        
        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.failed(self.failure)

        devicemap = self.lastargs[0]
        print devicemap
        assert type(devicemap) == types.DictType
        assert len(devicemap) == 1
        assert 'PseudoDevice' in devicemap
        assert len(devicemap['PseudoDevice']) == 2
        assert 'Device1' in devicemap['PseudoDevice']
        assert 'Device2' in devicemap['PseudoDevice']



    def test_device_execute(self):
        """Proxy forward command to correct DeviceServer"""

        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "executing remote setParameter timed out ... failing")

        # 3-digit random integer
        value = int(random.random()*1000)
	
	# get a device key for use in next step
	self.done = False
	d = self.aggregator.getDeviceList()
	d.addCallback(self.succeeded)
	d.addErrback(self.failed)

	while not self.done:
	    reactor.iterate(0.1)

	if self.failure:
	    self.fail(self.failure)

	print
	print "DEBUG:"
	device = self.lastargs[0][0]
	print device.name

        # store number in 'remote' PseudoDevice
        d = self.aggregator.deviceExecute(device, 'setParameter', value)
        assert isinstance(d, defer.Deferred)
        d.addCallback(self.succeeded)
        
        # idle until code above triggers succeeded or timeout causes failure
        self.done = False
        while not self.done:
            reactor.iterate(0.1)
        
        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.failed(self.failure)


        # safety timeout
        self.timeout = reactor.callLater(10, self.failed, "executing remote getParameter timed out ... failing")

        # store number in 'remote' PseudoDevice
        d = self.aggregator.deviceExecute(device, 'getParameter')
        assert isinstance(d, defer.Deferred)
        d.addCallback(self.succeeded)
        
        # idle until code above triggers succeeded or timeout causes failure
        self.done = False
        while not self.done:
            reactor.iterate(0.1)
        
        # will arrive here eventually when either succeeded or failed method has fired
        if self.failure:
            self.failed(self.failure)

        returnvalue = self.lastargs[0]
        assert returnvalue == value


    if False:
        test_handled_configurator = True
        test_devicelist_as_deferred = True
        test_devicemap_as_deferred = True
        test_device_execute = True
        test_password = True
