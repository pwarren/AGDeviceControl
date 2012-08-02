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
from agdevicecontrol.devices import agserial
AGSerial = agserial.AGSerial
AGSerialError=agserial.AGSerialError

from twisted.trial import unittest

class TestAGSerial(unittest.TestCase):

    def setUpClass(self):
	import serial
	import sys
	if sys.platform == 'darwin':
	    raise unittest.SkipTest, "Not running test on Darwin (OS X)"
	
    def test_interface(self):
	"""We need read and write to a shared serial port"""
	
	dummy_port = AGSerial(0)
	assert hasattr(dummy_port,"write")
	assert hasattr(dummy_port,"read")
        assert hasattr(dummy_port,"setTimeout")

    def test_double_instantiation(self):
	port_1 = AGSerial(1,
		  baudrate = 9600,                
		  bytesize = agserial.EIGHTBITS,    
		  parity = agserial.PARITY_NONE,    
		  stopbits = agserial.STOPBITS_ONE, 
		  timeout = 0.1,                  
		  xonxoff = 0,                    
		  rtscts = 1)


	port_2 = AGSerial(1,
		  baudrate = 9600, 
		  bytesize = agserial.EIGHTBITS,
		  parity = agserial.PARITY_NONE,
		  stopbits = agserial.STOPBITS_ONE,
		  timeout = 0.1,                 
		  xonxoff = 0,                   
		  rtscts = 1)

	assert port_1 == port_2

    def test_different_args_same_port(self):
	port_1 = AGSerial(1,
		  baudrate = 9600,                
		  bytesize = agserial.EIGHTBITS,    
		  parity = agserial.PARITY_NONE,    
		  stopbits = agserial.STOPBITS_ONE, 
		  timeout = 0.1,                  
		  xonxoff = 0,                    
		  rtscts = 1)

	self.failUnlessRaises(AGSerialError,AGSerial,1,
			      baudrate = 566000,                
			      bytesize = agserial.EIGHTBITS,    
			      parity = agserial.PARITY_NONE,    
			      stopbits = agserial.STOPBITS_ONE, 
			      timeout = 0.1,                  
			      xonxoff = 0,
			      rtscts = 1)

# not sure how to test read/write.

