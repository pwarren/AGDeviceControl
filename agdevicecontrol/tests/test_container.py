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
from agdevicecontrol.common.container import Container
from agdevicecontrol.tests.subprocessprotocol import SubProcessProtocol

from twisted.internet import defer, reactor
from twisted.test.test_process import SignalMixin
from twisted.trial import unittest
from twisted.spread.jelly import jelly
from twisted.spread import pb
from copy import copy
import types
import os
import time
import sys
#from twisted.python import log
#log.startLogging(sys.stdout)

class TestContainer(SignalMixin, unittest.TestCase):

    def setUpClass(self):

	self.csProcess = SubProcessProtocol()
	self.csProcess.waitOnStartUp(['container_server.py'], \
				     path = os.path.join(agdevicecontrol.path,'tests'))
		
	print "csProcess started"
	time.sleep(1)

    def tearDownClass(self):
	print "tearDownClass"
	self.csProcess.waitOnShutDown()

    def setUp(self):
	print
	print "setUP"
	self.done = False
	self.failure = None


    def succeeded(self, *args):
        """Allow reactor iteration loop in test proper to exit and pass test"""
	self.done = True
	self.timeout.cancel()  # safety timeout no longer necessary
        self.lastargs = args  # make persistent for later checks


    def failed(self, reason):
        """Allow reactor iteration loop in test proper to exit and fail test"""
	print 
	print "DEBUG: failed"
        self.done = True
        self.failure = reason
        self.lastargs = None

#----------------------------------------------------------------------	

    def test_hashable(self):
        """Containers need to be hashable"""
        b = Container()
        assert hash(b)


    def test_hashable(self):
        """Comparison for equality"""

        b1 = Container()
        b1.name = 'Device1'
        b2 = copy(b1)
        
        self.assertEqual(b1,b2)


    def test_attributes(self):
        """Can iterate over previously set attributes of container"""

        b = Container()
        b.int = 1234
        b.float = 3.14
        b.string = "sample string"
        


    def test_serializable(self):
        """Confirm containers can travel the wire"""

        b = Container()
        b.name = 'Device'
        b.type = 'PseudoDevice'
        b.description = "A string describing this device"

        # Jelly is the low-level serializer of the twisted framework
        assert jelly(b)


    def test_unique_ids(self):
        """Confirm that reasonably large number of discrete containers all get unique ids"""

        ids = []
        instances = []
        for i in range(1000):
            instance = Container()
            assert instance.id not in ids
            ids.append(instance.id)
            instances.append(instance)


    def test_zzz_echo_tcp(self):
	"""Test container can travel over a TCP connection"""
	# safety timeout
        self.timeout = reactor.callLater(5, self.failed, "Something Bad happened... Bailing")
	
	factory = pb.PBClientFactory()
	reactor.connectTCP("localhost",8800, factory)
	deferred = factory.getRootObject()
	deferred.addCallback(self._got_reference)
	deferred.addErrback(self.failed)

	while self.done is False:
	    reactor.iterate(0.1)

	if self.failure:
	    self.fail(self.failure)	

    def _got_reference(self, remote):
	self.remote = remote
	d = self.remote.callRemote("get_bucket")
	d.addCallback(self.succeeded)
	d.addErrback(self.failed)

