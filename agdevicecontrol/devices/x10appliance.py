
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

"""Concrete class for x10 appliance module
instantiate with (serial port, House, Number)
ie, (0,A,1)
"""

from switch import Switch

import serial
import struct
import time


# X10 protocol allows 16 "houses" with 16 devices each
# For internal details, suggest downloading the "heyu"
# X10 driver for Linux which contains protocol.txt

housemap = {'A': '6',
            'B': 'E',
            'C': '2',
            'D': 'A',
            'E': '1',
            'F': '9',
            'G': '5',
            'H': 'D',
            'I': '7',
            'J': 'F',
            'K': '3',
            'L': 'B',
            'M': '0',
            'N': '8',
            'O': '4',
            'P': 'C'}

devicemap = {1: '6',
             2: 'E',
             3: '2',
             4: 'A',
             5: '1',
             6: '9',
             7: '5',
             8: 'D',
             9: '7',
             10: 'F',
             11: '3',
             12: 'B',
             13: '0',
             14: '8',
             15: '4',
             16: 'C'}


class X10Appliance(Switch):

    def __init__(self, *args, **kwargs):
        Switch.__init__(self, *args, **kwargs)

        if type(self.number) == type(''):
            self.number = eval(self.number)
        
        self.house = housemap[self.house.capitalize()]
        self.number = devicemap[self.number]

        self.port = int(self.port)

        # start in off state, must be a way of determining device State ..
        self._power = 'Off'

        try:
            self._port = serial.Serial(self.port,
                                       baudrate = 4800,
                                       bytesize = serial.EIGHTBITS,
                                       parity = serial.PARITY_NONE, 
                                       stopbits = serial.STOPBITS_ONE,
                                       timeout = 1,
                                       xonxoff = 0,
                                       rtscts = 0)
        except serial.SerialException:
            self._port = None


    def getPower(self):
        return self._power


    def setPower(self,value):
        if value == None:
            return
        if 'On' in value:
            cmd = struct.pack('2B',
                              0x80 + int(self.house,16),
                              int('0x' + self.house + '2',16))
            
            self._power = 'On'
            self._send(cmd)
            time.sleep(1.0)

        
        else:
            cmd = struct.pack('2B',
                              0x80 + int(self.house,16),
                              int('0x' + self.house + '3',16))
            self._power = 'Off'
            self._send(cmd)
            time.sleep(1.0)
            
            

    #------ private methods -----------------------------------------------

    def _send(self,cmd):

        sync = struct.pack('B',0x00)

        # 2 byte string identifying the house/device combination
        self._device = struct.pack('2B',0x04,
                                   int('0x' + self.house + self.number,16))

        #send device identifier
        self._port.write(sync + self._device)
        self._port.read(30)

        #send 'clear'
        self._port.write(sync)
        time.sleep(0.5)
        self._port.read(30)
        
        #send command
        self._port.write(cmd)
        self._port.read(30)

        #send 'clear'
        self._port.write(sync)
        time.sleep(0.5)
        self._port.read(30)



    _heyu_output = """
        heyu on a1     Address = 0x04, 0x66  cmd = 0x06,0x62
        heyu off a1    Address = 0x04, 0x66  cmd = 0x06,0x63

        heyu on b1     Address = 0x04, 0xe6 cmd = 0x06,0xe2
        heyu off b1    Address = 0x04, 0xe6 cmd = 0x06,0xe3


        heyu on b2     Address = 0x04, 0xee cmd = 0x06,0xe3
        heyu off b2    Address = 0x04, 0xe6 cmd = 0x06,0xe3

        """


    _active_home_output = """

        on a1 sequence:
        S  0x00 0x04 0x66
        R  0x6A
        S  0x00
        R  0x55
        
        S  0x06 0x62
        R  0x68
        S  0x00
        R  0x55

        on a2:
        
        0x00 0x04 0x6E
        0x72
        0x00
        0x55
        0x06 0x62
        0x68
        0x00
        0x55

        off A1

        0x00 0x04 0x66
        0x6A
        0x00
        0x55
        0x06 0x63
        0x69
        0x00
        0x55

        off A2
        
        0x00 0x04 0x6E
        0x72
        0x00
        0x55
        0x06 0x63
        0x69
        0x00
        0x55
        """
