
# -*- test-case-name: agdevicecontrol.test.test_transport -*-
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


def encode(name, ip, port, passwd):
    return '%s::%s::%s::%s' % (name, ip, port, passwd)


def decode(msg):
    tmp = msg.split('::')
    if len(tmp) != 4:
        raise ValueError
    
    name = tmp[0]
    ip = tmp[1]

    # might throw a ValueError ...
    port = int(tmp[2])

    passwd = tmp[3]

    return (name, ip, port, passwd)
