#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_configurator -*-
#
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
from zope.interface import implements, Interface
from twisted.python import components

from ConfigParser import SafeConfigParser
from StringIO import StringIO
import os, os.path



class IConfigurator(Interface):

    def createDevice(devicename):
        """Instantiate named device with arguments from the parsed configuration file"""

    def getPassword():
        """Returns string password from config [authentication] section, None if missing"""



class Configurator(SafeConfigParser):
    """.ini-style parsing of DeviceServer config with device factory ability"""

    implements(IConfigurator)

    def __init__(self, s=None):
        SafeConfigParser.__init__(self)  # baseclass constructor

        if type(s) == type(''):
            if os.path.isfile(s):  # passed a config filename
                s = open(s).read()
            else:
                raise IOError, "File not found, %s" % s

        # default is open access
        self.password = ''

        if s is not None:
            self.fromString(s)


                

    def fromString(self, s):
        sfp = StringIO(s)  # file-like string buffer
        self.readfp(sfp)

        # convention that [authentication] section has password for this server
        for section in self.sections():
            if section.lower() == 'authentication':
                self.password = self.get(section, 'password')
                self.remove_section(section)
                break


    def getPassword(self):
        return self.password


    def __len__(self):
        return len(self.sections())

    def __contains__(self,x):
        return x in self.sections()


    def createDevice(self, name):
        
        # devices package has modules for each physical device
        base_module = __import__('agdevicecontrol.devices.' + self.get(name,'device').lower())

        base_module = getattr(base_module,'devices')
        
        # import devices.'name'
        device_module = getattr(base_module, self.get(name,'device').lower())

        # convention is that module devices.name has class Name,
        # we're after this callable ...

        # all module attributes
        device_module_attributes = dir(device_module)

        # filter out ones which aren't 'name'
        tmp = [attr for attr in device_module_attributes
               if self.get(name,'device').lower() in attr.lower()]

        # this is the callable Class ...
        device_class = getattr(device_module,tmp[-1])

        
        # get arguements from self
        tmpdict = {}
        for opt in self.options(name):
            tmpdict[opt] = self.get(name,opt)

        del tmpdict['device']

        # instantiate
        d = device_class(tmpdict)

        return name, d


#----------------------------------------------------------------------
if __name__ == "__main__":
    c = Configurator()
