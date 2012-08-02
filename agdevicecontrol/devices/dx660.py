
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
import sys
from device import DeviceError

try:
    import serial
except ImportError:
    if sys.platform == 'darwin':
        raise DeviceError, "Serial ports not supported on OS X"
    else:
        print "If you're on linux or windows, you shouldn't see this, please notify the developers at agdevicecontrol@anu.edu.au"
        raise DeviceError

import struct
import time
from switch import Switch

class DX660(Switch):
    """Driver for the Benq DX660 DLP projector"""
    
    def __init__(self, *args, **kwargs):
        Switch.__init__(self, *args, **kwargs)

        self._power=False
        
        try:
            self._port = serial.Serial(self.port,
                                       baudrate = 19200,
                                       bytesize = serial.EIGHTBITS,
                                       parity = serial.PARITY_NONE,
                                       stopbits = serial.STOPBITS_ONE,
                                       timeout = 0.1,
                                       xonxoff = 0,
                                       rtscts = 0)
        except serial.SerialException:
            self._port = None

            
    def setPowerOn(self):
        self._setPower('On')


    def setPowerOff(self):
        self._setPower('Off')


    def getPower(self):
        return self._power


    def isPowerOn(self):
        return self._power

        
    def isPowerOff(self):
        return not self._power


    #----- private methods ------------------------------------------------


    def _setPower(self,power):
        cmd = struct.pack('13B',
                          0xBE, 0xEF,
                          0x02,
                          0x06, 0x00,
                          0xE3, 0xCB,
                          0x9A,
                          0x00,0x00,0x00,0x00,0x00)
        if power == None:
            return
        if 'On' in power:
            self._power = True
            self._send(cmd)
            
        else:
            self._power = False
            self._send(cmd)
            time.sleep(0.2)
            self._send(cmd)




    def _send(self,cmd):
        
        # 2 byte string identifying the house/device combination
        self._port.write(cmd)
        
