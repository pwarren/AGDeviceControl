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


import socket
import agdevicecontrol
from agdevicecontrol.multicast.transport import encode, decode
from twisted.trial import unittest

class TestTransport(unittest.TestCase):

    def test_codec(self):
        """FIXME: this is a crude inflexible payload format"""

        name = 'localhost'
        ip = '127.0.0.1'
        port = 12345
        s = encode(name, ip, port, 'bkurk')

        assert type(s) == type('')

        dname, dip, dport, dpasswd = decode(s)
        assert dname == name
        assert dip == ip
        assert dport == port
        assert dpasswd == 'bkurk'


    def test_badformat(self):
        """Gracefully deal with bad payload format"""

        # expecting format as described in transport.py
        self.failUnlessRaises(ValueError, decode, socket.gethostname())

        
