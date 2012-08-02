#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_state -*-
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

import re

# custom dictionary that with known key ordering
from seqdict import seqdict

class State(seqdict):
    """Encapsulate a device's persistent 'state' in a sequential dictionary

    We use a sequential dictionary (one where the iterating over the
    keys is FIFO) to ensure that the 'Power' key is always first.
    """

    def __init__(self,s=None):
        self.list = []
        self.dict = {}

        if s is None:
            self['Power'] = None  # ensures first

        else:
            self.fromXML(s)

    def fromXML(self,s):
        # xml-like <name value="value"> regex
        pattern = re.compile( '<(?P<name>\w*) value="(?P<value>[\w\.,\[\]\(-?\) ]*)"/>' )
        matches = pattern.findall(s)
        for name,value in matches:
            try:
                self[name] = eval(value)  # try to convert string to tuple, float, int
            except NameError:
                self[name] = value  # otherwise assume it's a string


    def toXML(self):
        return repr(self)

    def iterkeys(self):
        return iter(self.keys())

    def fromFile(self,file_name):
        string = open(file_name).read()
        self.fromXML(string)

    def toFile(self,file_name):
        open(file_name,'w').write(repr(self))

    def clear(self):
        self.list = []
        self.dict = {}
        self['Power'] = None


    def __repr__(self):
        """XML-like string representation of current state"""

        # Example: <state><Power value="On" /></state>
        items = [ '<' + str(key)+ ' value="' + str(self[key]) + '"/>' for key in self.list ]

        # wrapped with common tags
        return "<state>" + "".join(items) + "</state>"
