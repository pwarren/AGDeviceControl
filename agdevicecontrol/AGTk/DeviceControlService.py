
#-----------------------------------------------------------------------------
# Name:        DeviceControlService.py
# Purpose:     Integrate AGDeviceControl package with the Access Grid
# Created:     2005/04/03
# Copyright:   (c) 2005 The Australian National University
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, os

if sys.platform == "darwin":
    # OSX: pyGlobus/globus need to be loaded before modules such as socket
    import pyGlobus.ioc

import time
import string

from AccessGrid.Types import Capability
from AccessGrid.AGService import AGService
from AccessGrid.AGParameter import OptionSetParameter, TextParameter

from AccessGrid import Platform
from AccessGrid.Platform.Config import AGTkConfig, UserConfig, SystemConfig
from AccessGrid.NetworkLocation import MulticastNetworkLocation
from AccessGrid.Platform import IsWindows, IsLinux, IsOSX

import agdevicecontrol
import agdevicecontrol.server.ports as ports


class DeviceControlService( AGService ):

    def __init__( self ):

        AGService.__init__( self )

        # making our service a PRODUCER tells the AGTk to allocate a venue multicast
        # address to communicate with other instances of this node service (need this
        # to find other Aggregators)
        self.capabilities = [ Capability( Capability.PRODUCER,
                                          "agdevicecontrol" ) ]

        # Set configuration parameters
        self.param_aggregator = OptionSetParameter( "aggregator", "Off", ["On", "Off"] )
        self.param_config = TextParameter( "aggregator config", "./aggregator.conf" )
        self.param_port = TextParameter( "aggregator port", str(ports.aggregator) )

        self.configuration.append(self.param_aggregator)
        self.configuration.append(self.param_config)
        self.configuration.append(self.param_port)

        if IsOSX():
            self.executable = "pythonw"  # ridiculous mac-ism
        else:
            self.executable = "python"



    def Start( self ):
        """Start service"""

        self.log.info("Entered DeviceControlService.Start method")

        if self.enabled:
            try:
                self.log.info("Starting DeviceControlService")
                self.log.info("Aggregator: %s" % self.param_aggregator.value)
                if self.param_aggregator.value == "On":
                    self.log.info("Creating local Aggregator")
                    options = "main.py --group %s --port %d --aggregator --aggregator-config %s --aggregator-port %s" \
                              % (self.host, self.port, self.param_config.value, self.param_port.value)
                else:
                    self.log.info("No local Aggregator, client only")
                    options = "main.py --group %s --port %d" % (self.host,self.port)

                self.log.info("%s %s" % (self.executable,options))
                self.processManager.StartProcess( self.executable, options.split() )
                self.started = 1

            except:
                self.log.exception("Exception in DeviceControlService.Start")
                raise Exception("Failed to start service")



    def Stop( self ):
        """Called on exiting a Venue *and* when the service is disabled"""

        self.log.info("Entered DeviceControlService.Stop method")

        if self.started:
            self.log.info("Stopping DeviceControlService")
            AGService.ForceStop(self)
            
        self.started = 0



    def ConfigureStream( self, streamDescription ):
        """Called when entering a venue with stream description (multicast address/port)"""

        self.host = streamDescription.location.host
        self.port = streamDescription.location.port

        self.log.info("DeviceControlService.ConfigureStream %s %s" % (self.host,self.port))

        if self.enabled:
            self.Start()



    def SetIdentity(self, profile):
        """Set the identity of the user driving the node"""
        self.log.info("SetIdentity: %s %s", profile.name, profile.email)


#---------------------------------------------------------------------
if __name__ == '__main__':

    from AccessGrid.AGService import AGServiceI, RunService

    port = int(sys.argv[1])
    service = DeviceControlService()
    serviceI = AGServiceI(service)
    RunService(service, serviceI, port)
