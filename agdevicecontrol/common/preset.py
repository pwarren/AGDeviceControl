#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_preset -*-
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


from agdevicecontrol.common.state import State
from ConfigParser import SafeConfigParser
import os.path


class Preset(dict):
    """A dictionary with keys as device names and values as device states.

    Can be written to and read from files which are easily human editable
    """

    def __init__(self, filename=None):
        dict.__init__(self)

        if filename is not None:
            self.fromFile(filename)


    def getNames(self):
        return self.keys()


    def toFile(self,filename):
        tmp = []
        for key in self.keys():
            string = '[' + key + ']\nstate: ' + self[key].toXML() +'\n'
            tmp.append(string)
        fp = open(filename,'w')
        fp.write(''.join(tmp))
        fp.close()


    def fromFile(self,filename):

        if not os.path.isfile(filename):
            raise IOError, 'Missing preset file %s' % filename

        parser = SafeConfigParser()
        parser.read(filename)
        for name in parser.sections():
            self[name] = State(parser.get(name,'state'))
        
