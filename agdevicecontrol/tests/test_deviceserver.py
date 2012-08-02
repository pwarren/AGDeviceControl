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
from agdevicecontrol.server.deviceserver import DeviceServer
from agdevicecontrol.server.configurator import Configurator
from twisted.internet import defer, reactor
from twisted.trial import unittest


configdata = """
# sample DeviceServer config file with placeholder devices

[Authentication]
password: bkurk
         
[Device1]
device: PseudoDevice
port: 1

[Device2]
device: PseudoDevice
port: 0
"""


debug = True


class TestDeviceServer(unittest.TestCase):

    def setUp(self):
        """I'm called at the very beginning of each test"""

        c = Configurator()
        c.fromString(configdata)
        self.ds = DeviceServer(c)

        self.finished = False
        self.failed = None
        self.pending_deferreds = []

        # safety timeout
        self.timeout = reactor.callLater(10, self.timedOut)



    def tearDown(self):
        """I'm called at the end of each test"""

        # spin here until all pending deferreds have fired (might
        # be overridden by time out of safety deferred)
        while len(self.pending_deferreds):
            if debug:
                print "test tearDown, waiting on %d deferreds" % len(self.pending_deferreds)
            reactor.iterate(0.2)


    def timedOut(self):
        """I'm called when the safety timer expires indicating test probably won't complete"""

        # FIXME: how do we cancel this test and cleanup remaining deferreds?
        self.pending_deferreds = []

        if debug:
            "**** timedOut callback, test did not complete"
        self.fail("Safety timeout callback ... test did not complete")
        reactor.crash()


    def successfulTest(self, returnvalue, d):
        """I'm a 'success' callback that allows a reactor.iterate loop to finish"""
        if debug:
            print "**** successfulTest callback: ", returnvalue, d
        assert d in self.pending_deferreds
        self.finished = True  # important
        self.failed = False  # important
        self.pending_deferreds.remove(d)
        if len(self.pending_deferreds) == 0:
            self.timeout.cancel()


    def failTest(self, returnvalue, d):
        """I'm a 'failure' callback that allows a reactor.iterate loop to finish"""
        if debug:
            print "**** failTest callback: ", returnvalue, d
        self.finished = True  # important
        self.failed = True  # important
        self.pending_deferreds.remove(d)
        if len(self.pending_deferreds) == 0:
            self.timeout.cancel()
        

    #---------- tests proper ------------------------------------

    def test_handled_configurator(self):
        """Deviceserver can be instantiated with a configurator rather than .conf filename"""
        assert 'Device1' in self.ds.config
        assert 'Device2' in self.ds.config
        assert self.ds.getPassword() == 'bkurk'
        
        self.timeout.cancel()


    def test_execute_returns_deferred(self):
        """Invoking commmands returns a twisted Deferred"""

	dev = self.ds.getDeviceList()[0]
	print
	print "DEBUG:"
	print dev.name, dev.type
	d = self.ds.deviceExecute(dev, 'delay', 2)
        assert isinstance(d, defer.Deferred)
        d.addCallback(self.successfulTest, d)
        self.pending_deferreds.append(d)


    def test_device_map(self):
        """Expected format for devicemap"""

        dm = self.ds.getDeviceMap()
        assert len(dm) == 1
        assert 'PseudoDevice' in dm
        assert len(dm['PseudoDevice']) == 2
        assert 'Device1' in dm['PseudoDevice']
        assert 'Device2' in dm['PseudoDevice']

        self.timeout.cancel()
