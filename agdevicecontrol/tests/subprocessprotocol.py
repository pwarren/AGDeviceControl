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
import agdevicecontrol
from twisted.internet import reactor, protocol, error
from twisted.trial import util


class SubProcessProtocol(protocol.ProcessProtocol):
    """I'm used to launch/control/report on a subprocess started during Trial testing"""

    done = False

    def __init__(self):
        self.data = ""
        self.running = None


    def outReceived(self, data):
        """Dribbles of stdout from Server child process"""
        self.data += data
        if "Starting factory" in data:  
            self.running = True
            self.timeout.cancel()
            self.timeout = None


    def outConnectionLost(self):
        if self.timeout:
            self.timeout.cancel()
        self.timeout = reactor.callLater(2, setattr, self, "running", False)


    def processEnded(self, reason):
        """tearDownClass waits until I'm called"""

        reactor.callLater(1, setattr, self, "done", True)

        # safety timeout might have been disabled by successful Server startup
        if self.timeout:
            self.timeout.cancel()

        print "--------- Server Output ----------------------------"
        print self.data




    def waitOnStartUp(self, arguments, path):
        self.timeout = reactor.callLater(10, setattr, self, 'running', False)
        reactor.spawnProcess(self, 'python', ['python'] + arguments,
                             env=os.environ, path=path)
    
        while self.running is None:
            print "server running: ", self.running
            reactor.iterate(0.1)


    def waitOnShutDown(self):
       if not self.done:
            try:
                self.transport.signalProcess('KILL')
                util.spinWhile(lambda: not self.done)
            except error.ProcessExitedAlready:
                pass
