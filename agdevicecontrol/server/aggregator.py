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
import os.path
import sys
import random
import string
from optparse import OptionParser

import agdevicecontrol
from agdevicecontrol.common import version, copyright
from agdevicecontrol.clients.connector import Connector, ConnectorError
from agdevicecontrol.server.configurator import Configurator
from agdevicecontrol.server.deviceserver import IDeviceServer
import agdevicecontrol.server.ports as ports
from agdevicecontrol.common import version

from twisted.spread import pb
from twisted.internet import defer, reactor
from twisted.cred import credentials, error
from twisted.cred.portal import Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.cred.portal import IRealm

if sys.platform == 'win32':
    import twisted.scripts._twistw as td
else:
    import twisted.scripts.twistd as td
from twisted.application import internet, service
from zope.interface import implements, Interface


class PBAggregator(pb.Avatar):
    """Exposes remote interface via persistent broker.

    Important to note that this class is instantiated for each connection.
    It should stay lightweight with all persistent state residing
    elsewhere.
    """

    def __init__(self, aggregator):
        self.aggregator = aggregator

    def perspective_getVersion(self):
        return version.version

    def perspective_getDeviceList(self):
        return self.aggregator.getDeviceList()

    def perspective_getDeviceMap(self):
        return self.aggregator.getDeviceMap()

    def perspective_deviceExecute(self, device, command, params=None):
        print "Aggregator perspective_deviceExecute: ", device, command, params
        return self.aggregator.deviceExecute(device, command, params)




#-----------------------------------------------------------------------
class IAggregator(Interface):

    def notifyOnMapped(callback):
        """I will ensure callback is notified when Aggregator has completed connections to constituent DeviceServers"""

    def getPassword():
        """I retrieve the random password created on instantation"""




#----------------------------------------------------------------------
class AggregatorRealm:
    """Portal uses this realm"""

    __implements__ = IRealm

    def __init__(self, a):
        self.a = a

    def requestAvatar(self, avatarId, mind, *interfaces):
        if pb.IPerspective in interfaces:
            avatar = PBAggregator(self.a)
            return pb.IPerspective, avatar, lambda:None
        else:
            raise NotImplementedError



#-----------------------------------------------------------------------
class Aggregator:

    implements(IDeviceServer,IAggregator)

    def __init__(self, config, testmode=False):

        self.servers = []

        # keyed by server, pbroot objects for RPC
        self.perspectives = {}

        # each server has a devicemap, each a dictionary keyed by devicetype
        # containing devices on the server
        self.devicemaps = {}

        # composite devicemap aggregating all deviceservers
        # by the devicetype, each a list of device names
        self.aggregatormap = {}

        # key by device name, corresponding server name containing the device
        self.devicedict = {}

        # becomes True only once we have perspectives on all DeviceServers
        self.connected = False

        # user can register to be informed when the Aggregator has completed
        # full connection to all constituent DeviceServers
        self._notifyonmappedcb = None

        # random password unless in testmode
        if not testmode:
            self.password = self._generatePassword()
        else:
            print "Test mode enabled with preconfigured password (shouldn't see this in normal use)"
            self.password = 'bkurk'  # hey, it had to be something ...

        # becomes True only once we have aggregatormap compiled
        self.mapped = False

        self.config = config
        if not isinstance(config,Configurator):
            self.loadConfig(config)

        self._connectAll()



    def _generatePassword(self, length=10):
        """http://mail.python.org/pipermail/python-list/2004-February/208169.html"""

        twoletters = [c+d for c in string.letters for d in string.letters]
        n = len(twoletters)
        l2 = length // 2
        lst = [None] * l2
        for i in xrange(l2):
             lst[i] = twoletters[int(random.random() * n)]
        if length & 1:
            lst.append(random.choice(string.letters))
        return "".join(lst)


    def getPassword(self):
        return self.password


    def notifyOnMapped(self, callback):
        self._notifyonmappedcb = callback


    def loadConfig(self, config_file):
        self.config = Configurator(config_file)


    def _connectAll(self):
        for server in self.config.sections():
            self._connect(server)


    def _connect(self, server):
        
        host = self.config.get(server,'host')
        port = int(self.config.get(server,'port'))

        factory = pb.PBClientFactory()
        reactor.connectTCP(host, port, factory)

        password = self.config.get(server,'password')
        d = factory.login(credentials.UsernamePassword(version.apiversion,password))

        d.addCallback(self._onConnectSuccess, server)
        d.addErrback(self._onConnectFailure, server)

        self.servers.append(server)


    def _onConnectSuccess(self, perspective, server):
        """I'm called on successful connection to each deviceserver 'server'"""

        self.perspectives[server] = perspective

        d = perspective.callRemote("getDeviceMap")
        d.addCallback(self._onDeviceMapSuccess, server)
        d.addErrback(self._onDeviceMapFailure, server)

        # have we got all the perspectives yet?
        if len(self.perspectives) == len(self.servers):
            self.connected = True
        

    def _onConnectFailure(self, failure, server):
        """Failed connection to a deviceserver"""

        # FIXME: notify of failure, have we finished getting perspectives?
        return failure



    def _onDeviceMapSuccess(self, devicemap, server):
        """I'm called on successful devicemap for every device server"""

        # paranioa check
        assert not server in self.devicemaps
	print server
    
        self.devicemaps[server] = devicemap

        for devicetype,devicelist in devicemap.items():
            if devicetype in self.aggregatormap:
                self.aggregatormap[devicetype].extend( devicelist )
            else:
                self.aggregatormap[devicetype] = devicelist

            # we'll need to discern server given a device name
            for device in devicelist:
		print " DEBUG:"
		print device.id
                assert not device in self.devicedict
                self.devicedict[device] = server

        # have we got all the devicemaps? (FIXME: can't complete if a
        # DeviceServer doesn't connect)
        if len(self.devicemaps) == len(self.servers):
            self.mapped = True
            if self._notifyonmappedcb:
                self._notifyonmappedcb(self)


    def _onDeviceMapFailure(self, failure, server):
        """Failed to retrieve a devicemap deviceserver"""
        return failure


    def getDeviceList(self):
        """Return aggregated devicelist (assumes built-up during connection chain"""
        return defer.succeed(self.devicedict.keys())


    def getDeviceMap(self):
        """Return aggregated devicemap (assumes built-up during connection chain"""
        return defer.succeed(self.aggregatormap)


    def deviceExecute(self, device, command, params=None):
	print 
	print "DEBUG:"
	print device
	print device.id
        server = self.devicedict[device]
        return self.perspectives[server].callRemote("deviceExecute", device, command, params)




def optionParser():
    """command line parameter processing"""

    parser = OptionParser(usage="%prog config-file [options]", version=copyright.version)

    parser.add_option("-p", "--port", action="store", type="int",
                      default=ports.aggregator,
                      dest="port",
                      help="Listen for client connections on this port")

    parser.add_option('-n', "--nodaemon", action="store_true",
                      dest="nodaemon", default=False,
                      help="Don't start as a daemon process")


    parser.add_option('-t', "--test", action="store_true",
                      dest="testmode", default=False,
                      help="Use known string as password")

    return parser.parse_args()




def create_portal(a):
    """I'm responsible for creating the authenticated portal"""
    realm = AggregatorRealm(a)
    portal = Portal(realm)
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(version.apiversion, a.getPassword())
    portal.registerChecker(checker)
    return portal
    

#-----------------------------------------------------------------------

# when run from command line (standalone mode)
if __name__ == "__main__":

    # duplicated below, needs to be hidden from a module import
    options, args = optionParser()

    if len(sys.argv) == 1:
        print "Must provide a valid config file as first argument.  Rerun with --help"
        sys.exit(1)

    if not os.path.isfile(sys.argv[1]):
        print "Config file '%s' does not exist.  Perhaps a fully qualified path?" % sys.argv[1]
        sys.exit(1)

    # free advertising ...
    print "[%s] %s" % (copyright.longversion, copyright.copyright)

    # run twistd with arguments
    tdcmds = ["-o", "-y", __file__]
    if options.nodaemon:
        tdcmds = ['--nodaemon',] + tdcmds
    tdoptions = td.ServerOptions()
    tdoptions.parseOptions(tdcmds)
    td.runApp(tdoptions)


elif __name__ == "__builtin__":  # don't execute when run from Trial (test_aggregator.py)

    # duplicated above, needs to be hidden from a module import
    options, args = optionParser()

    config = sys.argv[1]
    a = Aggregator(config, testmode=options.testmode)
    p = create_portal(a)

    # set up the application object - gets run when twistd loads this file
    application = service.Application('Aggregator')
    internet.TCPServer(options.port, pb.PBServerFactory(p)).setServiceParent(application)
