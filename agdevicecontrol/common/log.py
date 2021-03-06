#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_log -*-
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


try:  # uses bundled twisted
    import agdevicecontrol
except ImportError:
    import twisted
import twisted.python.log
import sys

# happens once on module import
twisted.python.log.startLogging(sys.stdout)

def write(message):
    twisted.python.log.msg(message)
