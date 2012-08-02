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
import time
from twisted.internet import defer, threads, reactor
from Queue import Queue
from zope.interface import implements, Interface


class IDeviceQueue(Interface):

    def submit(function, param):
        """Queue callable with parameters for execution"""



class DeviceQueue:

    implements(IDeviceQueue)


    def __init__(self):
        
        self.q = Queue()
        self.running = False
        self.starttime = time.time()


    def debug(self, s):
        print "%d %s" % (time.time()-self.starttime, s)
    

    def submit(self, function, param):

        self.debug( "submit: %s %s" % (function,param) )

        d = defer.Deferred()
        if self.running:
            self.debug( "queuing: %s %s " % (function, param) )
            self.q.put( (function,param,d) )
        else:
            self._runInThread(function, param, d)
        return d



    def _processQueue(self, result=None):

        self.debug("_processQueue: %s" % str(result))

        if self.q.empty():
            self.debug("empty Queue")
            self.running = False

        else:
            # next in queue ...
            function,param,d = self.q.get()
            self._runInThread(function, param, d)



    def _runInThread(self, function, param, d):
        """I run the function(param) in a thread adding callbacks to communicate result"""

        self.debug("threading: %s %s" % (function, param))
        self.running = True
        if param is None:
            threadd = threads.deferToThread(function)
        else:
            threadd = threads.deferToThread(function, param)
        threadd.pause()
        threadd.addCallback(d.callback)
        threadd.addCallback(self._processQueue)
        threadd.addErrback(self._error)
        threadd.addErrback(d.errback)
        threadd.unpause()


    def _error(self, failure):
        print "***** Error: ", str(failure)
        self._processQueue()
        return failure
    
    
if __name__ == '__main__':
    pass
