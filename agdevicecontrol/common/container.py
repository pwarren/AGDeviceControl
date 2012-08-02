#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_container -*-
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
from twisted.spread import pb
from twisted.spread import jelly
from zope.interface import implements, Interface
import socket


# in dotted network format
ip = socket.gethostbyname(socket.gethostname())


class IContainer(Interface):
    pass


class BaseContainer(pb.Copyable):
    """General purpose container"""

    implements(IContainer)


    def __init__(self):
	self.attributes = []
        self.id = hash("%s:%s" % (ip, self))

    def __hash__(self):
        return self.id


    def __copy__(self):
        c = Container()
        for a in self.attributes:
            c.set(a, getattr(self,a))
        c.id = self.id
        return c


    def set(self, name, value):
        if not name in self.attributes:
            self.attributes.append(name)
        setattr(self, name, value)


    def __eq__(self,other):
        """Define equality to be equality of attributes"""
        for a in self.attributes:
            try:
                if not getattr(self,a) == getattr(other,a):
                    return False
            except AttributeError:
                return False
        return True




class Container(BaseContainer, pb.Copyable, pb.RemoteCopy):
    pass


#class ReceiverContainer(Container, pb.RemoteCopy):
#    pass

pb.setUnjellyableForClass(Container, Container)


if __name__ == "__main__":

    b1 = Container()
    b1.set('name', 'Device1')
    b1.set('type', 'PseudoDevice')
    
    b2 = Container()
    b2.set('name', 'Device2')
    b2.set('type', 'Camera')
    
    b3 = copy(b1)

    print hash(b1)
    print hash(b2)
    print b1
