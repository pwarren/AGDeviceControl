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
import threading

try:
    import serial
except ImportError:
    if sys.platform == 'darwin':
        raise DeviceError, "Serial ports not supported on OS X"
    else:
        print "If you're on linux or windows, and you have installed pyserial,yo u shouldn't see this, please notify the developers at agdevicecontrol@anu.edu.au"  
        raise DeviceError


# wrap the attributes of pyserial as well

# Ugly, Ugly, Ugly!!


EIGHTBITS      = serial.EIGHTBITS
FCNTL          = serial.FCNTL
FIVEBITS       = serial.FIVEBITS
FileLike       = serial.FileLike
PARITY_EVEN    = serial.PARITY_EVEN
PARITY_NAMES   = serial.PARITY_NAMES
PARITY_NONE    = serial.PARITY_NONE
PARITY_ODD     = serial.PARITY_ODD
SEVENBITS      = serial.SEVENBITS
SIXBITS        = serial.SIXBITS
STOPBITS_ONE   = serial.STOPBITS_ONE
STOPBITS_TWO   = serial.STOPBITS_TWO
TERMIOS        = serial.TERMIOS
TIOCINQ        = serial.TIOCINQ
TIOCMBIC       = serial.TIOCMBIC
TIOCMBIS       = serial.TIOCMBIS
TIOCMGET       = serial.TIOCMGET
TIOCMSET       = serial.TIOCMSET
TIOCM_CAR      = serial.TIOCM_CAR
TIOCM_CD       = serial.TIOCM_CD
TIOCM_CTS      = serial.TIOCM_CTS
TIOCM_DSR      = serial.TIOCM_DSR
TIOCM_DTR      = serial.TIOCM_DTR
TIOCM_DTR_str  = serial.TIOCM_DTR_str
TIOCM_RI       = serial.TIOCM_RI
TIOCM_RNG      = serial.TIOCM_RNG
TIOCM_RTS      = serial.TIOCM_RTS
TIOCM_RTS_str  = serial.TIOCM_RTS_str
TIOCM_zero_str = serial.TIOCM_zero_str
XOFF           = serial.VERSION
XON            = serial.XON


#----------------------------------------------------------------------
class CachedSerialFactory:
    """Returns a new pyserial instance if not in existance, else returns the previously instantiated one"""
    
    
    # Basic ideas from http://www.norvig.com/python-iaq.html, see the
    # "Is no "news" good news?" section
    def __init__(self):
        self.cache={}
        self.cached_class = serial.Serial

    def __call__(self, port, *args, **kwargs):
        
        
        if self.cache.has_key(port):
            "we have an instance with this port"
            if self.cache[port]['args']==args and self.cache[port]['kwargs']==kwargs:
                return self.cache[port]['object']
            else:
                raise CachedSerialError, "Port taken by serial instance with different arguments"
        else:
            self.cache[port] = {}
            self.cache[port]['object'] = self.cached_class(port, *args, **kwargs)
            self.cache[port]['args']=args
            self.cache[port]['kwargs']=kwargs
            self.cache[port]['object'].sem = threading.Semaphore()
            return self.cache[port]['object']


SerialFactory = CachedSerialFactory()

#----------------------------------------------------------------------
class CachedSerialError(Exception):
    pass


#----------------------------------------------------------------------
class AGSerial:

    def __init__(self, port, *args, **kwargs):
        try:
            self.s_port = SerialFactory(port, *args, **kwargs)
        except CachedSerialError:
            raise AGSerialError
        
    def __eq__(self,other):
        if self.s_port == other.s_port:
            return 1
        else:
            return 0
        
        
    def read(length):
        self.s_port.sem.acquire()
        self._read,length
        self.s_port.sem.release()

    def write(line):
        self.s_port.sem.acquire()
        self.s_port.write(line)
        self.s_port.sem.release()

    def setTimeout(time):
        self.s_port.setTimeout(time)
    
    def _read(length):
        """Actually do the read from the serial port"""

        line = self.sport.read(length)
        self.s_port.mutex.unlock()
        return line

#----------------------------------------------------------------------

class AGSerialError(Exception):
    pass

#----------------------------------------------------------------------    
