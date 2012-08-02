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

import time
import agdevicecontrol
from agdevicecontrol.server.devicequeue import DeviceQueue
from agdevicecontrol.devices.device import DeviceError

from twisted.trial import unittest, util
from twisted.internet import reactor, defer


debug = True


def delay(seconds):
    time.sleep(seconds)
    return "Slept for %d seconds" % seconds

def raise_exception(seconds):
    time.sleep(seconds)
    raise DeviceError, "Slept for %s seconds and raised error" % seconds



class TestDeviceQueue(unittest.TestCase):

    def setUp(self):
        """I'm called at the beginning of each test"""
        self.q = DeviceQueue()
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


    def test_single_submission(self):
        """Submit single command to an empty queue"""

        # core API to test, the DeviceQueue
        d = self.q.submit(delay, 2)
        assert isinstance(d, defer.Deferred)
        d.addCallback(self.successfulTest, d)
        d.addErrback(self.failTest,d)

        self.pending_deferreds.append(d)

        while not self.finished:  # waiting for a deferred to fire ...
            reactor.iterate(0.2)
            if debug:
                print "test_queued_deferred, waiting on: ", self.failed, self.finished, len(self.pending_deferreds)
        
        # possibly set in failTest callback
        if self.failed:
            self.fail("Single submission test failed")



    def test_queued_commands(self):
        """Queued commands block and finish in order"""

        # core API to test, the DeviceQueue
        d1 = self.q.submit(delay, 4)
        d1.addCallback(self.successfulTest, d1)
        d1.addErrback(self.failTest,d1)

        d2 = self.q.submit(delay, 2)
        assert isinstance(d2, defer.Deferred)
        d2.addCallback(self.failTest, d2)
        d2.addErrback(self.failTest,d2)

        self.pending_deferreds.extend([d1,d2])

        while not self.finished:  # waiting for a deferred to fire ...
            reactor.iterate(0.2)
            if debug:
                print "test_queued_deferred, waiting on: ", self.failed, self.finished, len(self.pending_deferreds)
        
        # possibly set in failTest callback
        if self.failed:
            self.fail("Second submission finished first")



    def test_exception_wont_stall_queue(self):
        """Device exception shouldn't stall the queue"""

        d1 = self.q.submit(raise_exception, 1)
        d1.addCallback(self.successfulTest, d1)
        d1.addErrback(self.failTest,d1)
        
        d2 = self.q.submit(delay, 1)
        d2.addCallback(self.successfulTest, d2)
        d2.addErrback(self.failTest,d2)

        self.pending_deferreds.extend([d1,d2])

        while not self.finished:  # waiting for a deferred to fire ...
            reactor.iterate(0.2)
            if debug:
                print "test_queued_deferred, waiting on: ", self.failed, self.finished, len(self.pending_deferreds)



    if False:
        test_single_submission.skip = True
        test_queued_commands.skip = True
        test_exception_wont_stall_queue.skip = True
