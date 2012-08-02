## This is a twisted Application, run with:
##  $ twistd -noy container_server.py


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



import sys

from twisted.application import service, internet
from twisted.internet import reactor
from twisted.spread import pb

if sys.platform == 'win32':
    import twisted.scripts._twistw as td
else:
    import twisted.scripts.twistd as td

print __name__

import agdevicecontrol
from agdevicecontrol.common.container import Container

class Server(pb.Root):
    
    def __init__(self):
	self.bucket = Container()
	self.bucket.name = "BkUrK!"
	self.bucket.object = {1: "Blah", 2:"Chicken"}

    def remote_get_bucket(self):
	return self.bucket

    def remote_take_bucket(self, bucket):
	print "Got Bucket!"
	print bucket, hash(bucket)
	print "Name: ", bucket.name
	print "Object", bucket.object
	self.bucket = bucket

    def remote_shutdown(self):
	reactor.stop()



if __name__=='__main__':

    tdcmds = ["-n", "-o", "-y", __file__]

    tdoptions = td.ServerOptions()
    tdoptions.parseOptions(tdcmds)
    td.runApp(tdoptions)


else:
    application = service.Application("bucket_receiver")
    internet.TCPServer(8800, pb.PBServerFactory(Server())).setServiceParent(service.IServiceCollection(application))

