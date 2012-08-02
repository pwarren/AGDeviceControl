
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
        print "If you're on linux or windows, and you have installed pyserial,  you shouldn't see this, please notify the developers at agdevicecontrol@anu.edu.au"
        raise DeviceError

import struct
import time

from camera import Camera

class VCC4(Camera):
    """Canon VC-C4(R) concrete class

    Class for the Canon VC-C4 and VC-C4R Cameras.  See the Canon VC-C4
    Programmer's Manual for details on the structure and values for
    the RS232 commands.  If you are having trouble communicating with
    the camera, make sure that the self._startup() call in __init__ is
    uncommented.
    """
           
    def __init__(self, *args, **kwargs):
        """Takes arguments of serial port number (0-n) and camera
        number on daisy chain (1-9), a daisychain of 0 will send commands to
	all cameras on the port."""
	

        Camera.__init__(self, *args, **kwargs)

        # Some global values for the rs232 commands
        self._header = struct.pack('B',0xFF)
        self._footer = struct.pack('B',0xEF)

        self.sport = serial.Serial(self.port,                      #  port numbering starts at 0
                                   baudrate = 9600,                #
                                   bytesize = serial.EIGHTBITS,    #
                                   parity = serial.PARITY_NONE,    #
                                   stopbits = serial.STOPBITS_ONE, #
                                   timeout = 0.1,                  #
                                   xonxoff = 0,                    #  disablesoftware flow control
                                   rtscts = 1)                     # enable hardware flow control
	
        self.port = self._toParm(self.port,1)
        
	self.daisychain  = self._toParm(int(self.daisychain),1)
        self._dev  = struct.pack('2B',
                                 0x30,
                                 0x30+int(self.daisychain,16))
	
        self.movement_quanta=10
	

	if self.daisychain ==  "1": 
	    # if we're the first camera on the chain:
	    self._startup()  # comment out for speedier testing
        

                        
    def _startup(self):
        "sets the camera up for use"
       
        # Cascade Off
        #command = struct.pack('2B',0x00,0x8F)
        #parameter = struct.pack('B',0x30)
        #self._send(command,parameter)
        
        # Cascade On
        dev = struct.pack('2b',0x30,0x30)
        command = struct.pack('2B',0x00,0x8F)
        parameter = struct.pack('B',0x31)
        self.sport.write(
            self._header +
            dev +
            command +
            parameter +
            self._footer)
        time.sleep(1)
        line = self._read()
	print "DEBUG: ", line
	
        # Put into host control mode
        time.sleep(1)
        self.hostControlMode()
        
        # Turn camera On
        self.setPowerOn()

        # Command Termination Notification Off!
        command = struct.pack('2B',0x00,0x94)
        parameter = struct.pack('B',0x30)
        self._send(command,parameter)

                
        # Auto Focus On
        command = struct.pack('2B',0x00,0xA1)
        parameter = struct.pack('B',0x30)
        self._send(command,parameter)

        # initialise pedestal
        command = struct.pack('2B',0x00,0x58)
        parameter = struct.pack('B',0x30)
        self._send(command,parameter)
        time.sleep(3)

        # move to Wide Angle Zoom
        self.setZoom(0)
        time.sleep(5)

        # clear out any unread bytes
        self._read()
        self._read()
        self._read()


    # State Commands

    def isPowerOn(self):
        command = struct.pack('2B',0x00,0x86)
        parameter = struct.pack('B',0x30)
        line = self._send_request(command,parameter)
        print "Debug: " + line
        line = line[-3]
        if line == '0':
            return True
        else: # line == 2
            return False


    def isPowerOff(self):
        command = struct.pack('2B',0x00,0x86)
        parameter = struct.pack('B',0x30)
        line = self._send_request(command,parameter)
        print "Debug: " + line
        line = line[-3]
        if line == '0':
            return False
        else: # line == 2
            return True
    
    def setPowerOn(self):
        "Set the Power Status (Turn on of Off) (0|1)"
        command = struct.pack('2B',0x00,0xA0)
        parameter = struct.pack('B',0x31)
        line = self._send(command,parameter)
        time.sleep(8)
        return line


    def setPowerOff(self):
        "Set the Power Status (Turn on of Off) (0|1)"
        command = struct.pack('2B',0x00,0xA0)
        parameter = struct.pack('B',0x30)
        line = self._send(command,parameter)
        time.sleep(8)
        return line

    

    def getPosition(self):
        """Returns Current Camera Angles (x,y)"""
        command = struct.pack('2B',0x00,0x63)
        line = self._send_request(command,'')
        print "Debug:" + line
        line = line[5:-1]
        tmpP = line[:4]
        tmpT = line[4:8]
        tmpP = int( (int(tmpP,16) - 0x8000) * 0.1125 )
        tmpT = int( (int(tmpT,16) - 0x8000) * 0.1125 )
        return (tmpP,tmpT)

    def setPosition(self,(x,y)):
        """Moves Camera to given angles x and y
        For VC_C4R: -164 < x < 164, -90 < y < 10
        For VC-C4:  -100 < x < 100, -40 < y < 30"""

        # check the values are sensible.
        if self._CamTypeRequest() == 'VC-C4':
            if (x > 100 or x < -100):
                raise self.RangeWarning, "x Parameter Out of Range (-100 -> 100)"
            if (y > 30 or y < -40):
                raise self.RangeWarning, "y Parameter Out of Range (-40 -> 30)"
        else:
            if (x > 164 or x < -164):
                raise self.RangeWarning, "x Parameter Out of Range (-164 -> 164)"
            if (y > 9 or y < -90):
                raise self.RangeWarning, "y Parameter Out of Range (-90 -> 10)"

        command = struct.pack('2B',0x00,0x62)

        # Oddness with the camera! (Or My code???) FIXME: explain
        # to make a getPosition() == the previous setPosition()
        # these offsets are needed.
        if x > 0: x += 1
        if y > 0: y += 1
        
        # format parameters.
        tmp1 = int(0x8000 + x//0.1125)
        tmp2 = int(0x8000 + y//0.1125)

        parameter = self._toParm(tmp1,4) + self._toParm(tmp2,4)
        return self._send(command,parameter)
            
    def getZoom(self):
        command = struct.pack('2B',0x00,0xA4)
        line = self._send_request(command,'')
        line = int(line[-3:-1],16)
        value = round(line / 128.0,3)
        return value

    def setZoom(self,Zoom):
        if not ((Zoom <= 1.0) and (Zoom >= 0)):
            raise self.RangeWarning, "Zoom out of Range"
        command = struct.pack('2B',0x00,0xA3)

        #set appropriate PanTilt speed and Quanta
        speed = self._getSpeedFromZoom(Zoom)
        self.setSpeed(speed)
        self.movement_quanta = self._getQuantaFromZoom(Zoom)

        Zoom = int(round(128.0 * Zoom))
        parameter = self._toParm(Zoom,2)
        return_value =  self._send(command,parameter)
        
        #Adjust Zoom to match the values a VCC4 Expects:
                
        return return_value

    # pedestal turn rates
    
    def setPanSpeed(self,(Speed)):
        if not ((Speed <= 1.0) and (Speed >= 0)):
            raise self.RangeWarning, "Speed out of Range"
        command = struct.pack('2B',0x00,0x50)
        
        #Adjust Speed to match the values a VCC4 Expects:
        #range(8,800)
        Speed = int(round(792.0 * Speed) + 8.0)
        parameter = self._toParm(Speed,3)
        return self._send(command,parameter)


    def getPanSpeed(self):
        command = struct.pack('2B',0x00,0x52)
        parameter = struct.pack('B',0x30)
        line = self._send_request(command,parameter)
        line = int(line[-4:-1],16)
        value = round( (line-8.0)/792.0 ,3)
        return value


    def setTiltSpeed(self,(Speed)):
        if not ((Speed <= 1.0) and (Speed >= 0)):
            raise self.RangeWarning, "Speed out of Range"
        command = struct.pack('2B',0x00,0x51)
        
        #Adjust Speed to match the values a VCC4 Expects:
        #range(8,622)
        Speed = int(round(614.0 * Speed) + 8.0)
        parameter = self._toParm(Speed,3)
        return self._send(command,parameter)

    def getTiltSpeed(self):
        command = struct.pack('2B',0x00,0x52)
        parameter = struct.pack('B',0x31)
        line = self._send_request(command,parameter)
        line = int(line[-4:-1],16)
        value = round( (line-8.0)/614.0 ,3)
        return value


    def getSpeed(self):
        return self.getPanSpeed()

    def setSpeed(self,speed):
        #print "DEBUG: Setting Speed", speed
        self.setPanSpeed(speed)
        self.setTiltSpeed(speed)

    #verb commands

    def PanLeftStart(self):
        command = struct.pack('2B',0x00,0x53)
        parameter = struct.pack('B',0x32)
        return self._send(command,parameter)
        
    def PanRightStart(self):
        command = struct.pack('2B',0x00,0x53)
        parameter = struct.pack('B',0x31)
        return self._send(command,parameter)

    def TiltUpStart(self):
        command = struct.pack('2B',0x00,0x53)
        parameter = struct.pack('B',0x33)
        return self._send(command,parameter)

    def TiltDownStart(self):
        command = struct.pack('2B',0x00,0x53)
        parameter = struct.pack('B',0x34)
        return self._send(command,parameter)

    def PanTiltStop(self):
        command = struct.pack('2B',0x00,0x53)
        parameter = struct.pack('B',0x30)
        line =  self._send(command,parameter)
        time.sleep(0.2)
        return line

    # convenience for diagonal motion

    def PanLeftTiltUpStart(self):
        self.TiltUp()
        self.PanLeft()

    def PanRightTiltUpStart(self):
        self.TiltUp()
        self.PanRight()
        
    def PanLeftTiltDownStart(self):
        self.TiltDown()
        self.PanLeft()

    def PanRightTiltDownStart(self):
        self.TiltDown()
        self.PanRight()


    #Zoom
    
    def ZoomInStart(self):
        command = struct.pack('2B',0x00,0xA2)
        parameter = struct.pack('B',0x34)
        return self._send(command,parameter)
    
    def ZoomOutStart(self):
        command = struct.pack('2B',0x00,0xA2)
        parameter = struct.pack('B',0x33)
        return self._send(command,parameter)
    
    def ZoomStop(self):
        command = struct.pack('2B',0x00,0xA2)
        parameter = struct.pack('B',0x30)
        return_value =  self._send(command,parameter)
        zoom = self.getZoom()
        #print "DEBUG: Zoom = ",zoom
        speed = self._getSpeedFromZoom(zoom)
        self.setSpeed(speed)
        self.movement_quanta = self._getQuantaFromZoom(zoom)
        return return_value



    #quantised verb commands

    def PanLeft(self):
        self.moveRelative(-self.movement_quanta,0)
        
    def PanRight(self):
        self.moveRelative(self.movement_quanta,0)
        
    def TiltUp(self):
        self.moveRelative(0,self.movement_quanta)
        
    def TiltDown(self):
        self.moveRelative(0,-self.movement_quanta)
        
    # convenience for diagonal motion

    def PanLeftTiltUp(self):
        self.moveRelative(-self.movement_quanta,self.movement_quanta)
        
    def PanRightTiltUp(self):
        self.moveRelative(self.movement_quanta,self.movement_quanta)
                        
    def PanLeftTiltDown(self):
        self.moveRelative(-self.movement_quanta,-self.movement_quanta)
                
    def PanRightTiltDown(self):
        self.moveRelative(self.movement_quanta,-self.movement_quanta)


    def moveRelative(self,Pan,Tilt):
        tmp = self.getPosition()
        cPan, cTilt = tmp[0], tmp[1]
        self.setPosition( (cPan + Pan, cTilt+Tilt) )



    def ZoomIn(self):
        self.zoom_relative("In")
    
    def ZoomOut(self):
        self.zoom_relative("Out")


    def zoom_relative(self,direction):

        if "In" in direction:
            self.setZoom(min(self.getZoom()+0.1,1.0))

        if "Out" in direction:
            self.setZoom(max(self.getZoom()-0.1,0.0))

                
    #Home
    
    def MoveHome(self):
        """Move the camera to (0,0)"""
        command = struct.pack('2B',0x00,0x57)
        return self._send(command,'')


    # Control Modes
           
    def hostControlMode(self):
        "Control by PC"
        command = struct.pack('2B',0x00,0x90)
        parameter = struct.pack('B',0x30)
        self._send(command,parameter)
        time.sleep(0.5)

    def localControlMode(self):
        "Control by IR Remote"
        command = struct.pack('2B',0x00,0x90)
        parameter = struct.pack('B',0x31)
        self._send(command,parameter)
        time.sleep(0.5)


    # private methods    

    def _ParseReturn(self,line):
        ErrorCode=line[3:5]#
        # Should probably have a dictionary for this!"
        if str(ErrorCode) == "00":
            # Do Nothing for "OK"
            pass
        elif str(ErrorCode) == '':
            pass
        elif str(ErrorCode) == "90":
            raise self.ModeWarning, "Not In Host Control Mode"
        elif str(ErrorCode) == "10":
            self.BusyWarning, "Busy"
        elif str(ErrorCode) == "50":
            self.BusyWarning, "Busy Or Incorrect Parameters"
        elif str(ErrorCode) == "30":
            # This should never happen. Useful for testing tho.
            raise self.UnkownCommandWarning, "Invalid Command"
        else:
            return "Unkown Error Code: '" + line + "'"
        
    def _CamTypeRequest(self):
        command = struct.pack('2B',0x00,0x5C)
        parameter = struct.pack('B',0x33)
        self.sport.write(self._header + self._dev + command + parameter + self._footer)
        line = self._read()
        if len(line) < 20: self._ParseReturn(line)
        line = int(line[5:-1],16) - 0x8000
        if line == 800:
            return "VC-C4"
        else:
            return "VC-C4R"
        

    def _read(self):
        return self.sport.read(30)

    def _send(self,cmd,parm):
        """Send a command over the serial port"""
        self.sport.write(
            self._header +
            self._dev +
            cmd +
            parm +
            self._footer)

        try:
            line = self._ParseReturn(self._read())
        except self.ModeWarning:
                self.hostControlMode()
                return self._send(cmd,parm)
        return line

    def _send_request(self,cmd,parm):
        """Send an Information Request command over the serial port"""
        self.sport.write(
            self._header +
            self._dev +
            cmd +
            parm +
            self._footer)
        
        line = self._read()
        if len(line) <= 6:
            try:
                return self._ParseReturn(line)
            except self.ModeWarning:
                self.hostControlMode()
                return self._send_request(cmd,parm)
                
        else:
            return line

    def _toParm(self,parameter,size):
        """Returns the VCC control Code for the integer 'parameter'
        eg, parameter = 9, result=0x30,0x35"""
        tmp=[]
        hex_string = hex(parameter)
        hex_string = hex_string[hex_string.find('x')+1:]

        if len(hex_string) < size:
            for i in range (0,size-(len(hex_string))):
                hex_string = '0' + hex_string
                
        for i in range(0,size):
            if int(hex_string[i],16) < 10:
                tmp.append( int( '0x'+ str(30 + int(hex_string[i],16)),16) )
            else:
                tmp.append( int( '0x'+ str(31 + int(hex_string[i],16)),16) )
        return_string = ''
        for i in range(0,size):
            return_string = return_string + struct.pack('B',tmp[i])
        return return_string


    def _getSpeedFromZoom(self,Zoom):
        #print "DEBUG: Zoom =", Zoom
        speed = (1.0-Zoom)/2.0
        #print "DEBUG: Speed=", speed
        
        return speed


    def _getQuantaFromZoom(self,Zoom):
        # adjust has been emperically determined, adjust to suit
        adjust = 5
        if Zoom == 1.0:
            #adjust for boundary
            movement_quanta = 1
        else:
            movement_quanta = adjust - (adjust*Zoom)

        return movement_quanta
