
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
        print "If you're on linux or windows, and you have installed pyserial, you shouldn't see this, please notify the developers at agdevicecontrol@anu.edu.au"
        raise DeviceError


import struct
import time

from camera import Camera


class VISCA(Camera):
    """VISCA camera communication protocol

    This class should work for all sony cameras that follow the VISCA command protocol
    This includes:
      EVI-D30
      EVI-D31
      EVI-D100/D100P
      EVI-D70/D70P

    Info taken from the evid30 commandlist published by sony at:
    http://www.sony.net/Products/ISP/products/ptz/EVID30.html
    """
           
    def __init__(self, *args, **kwargs):
        """Takes arguments of serial port number (port=0-n) and camera
        number on daisy chain (daisychain=1-7) """

        Camera.__init__(self, *args, **kwargs)

        self.port = int(self.port)
        self.daisychain = int(self.daisychain)
        
        # Header, which camera we're talking to
        self._header = struct.pack('B',0x80+self.daisychain)

        #modes
        self._mode_control = struct.pack('B',0x01)
        self._mode_info    = struct.pack('B',0x09)
        self._mode_net     = struct.pack('B',0x00)

        #categorys (not rigidly defined in spec
        self._category_move = struct.pack('B',0x06)
        self._category_cam = struct.pack('B',0x04)
        
        # End of command
        self._terminator = struct.pack('B',0xFF)

        # set up the serial port
        self.sport = serial.Serial(self.port,                        
                                   baudrate = 9600,                
                                   bytesize = serial.EIGHTBITS,    
                                   parity = serial.PARITY_NONE,    
                                   stopbits = serial.STOPBITS_ONE, 
                                   timeout = 0.1,                  
                                   xonxoff = 0,                      
                                   rtscts = 1)

        self.movement_quanta=10
        # movement speed
        # to be controlled by Zoom eventually
        self._panSpeed = struct.pack('B',0x09)
        self._tiltSpeed = struct.pack('B',0x09)
        self._startup
        self._read()
        self._read()
        self._read()
                        
    def _startup(self):
        "sets the camera up for use"

        self.setPower("On")

        # AddressSet
        self._send(struct.pack('4B',0x88,0x30,0x01,0xFF))

        #IF_Clear
        self._send(struct.pack('5B',0x88,0x01,0x00,0x01,0xFF))

        # pedastal reset
        self._send(struct.pack('5B',0x88,0x01,0x06,0x05,0xff))



    # Power

    def isPowerOn(self):
        "Return the Current Power status (On|Off)"
        command = struct.pack('B',0x00)
        
        line = self._send_cam_inq(command)

        if struct.unpack('4B',line)[2] == 2:
            return True
        else:
            return False

    def isPowerOff(self):
        "Return the Current Power status (On|Off)"
        command = struct.pack('B',0x00)
        
        line = self._send_cam_inq(command)
        
        if struct.unpack('4B',line)[2] == 2:
            return False
        else:
            return True
        
    def setPowerOn(self):
        "Set the Power Status (Turn on or Off) (0|1)"
        command = struct.pack('B',0x00)
        parameter = struct.pack('B',0x02)
        line = self._send_cam(command+parameter)
        return line

    def setPowerOff(self):
        "Set the Power Status (Turn on or Off) (0|1)"
        command = struct.pack('B',0x00)
        parameter = struct.pack('B',0x03)
        line = self._send_cam(command+parameter)
        return line
            
    # Position
    
    def getPosition(self):
        """Returns Current Camera Angles (x,y)"""
        command = struct.pack('B',0x12)
        line = self._send_move_inq(command)

        line = line[2:-1]
                
        x = line[:4]
        y = line[4:]

        x = self._convert_position(x)
        y = self._convert_position(y)

        return (int((x/862.0)*90),int((y/280.0)*30))


    def setPosition(self,(x,y)):
        """Moves Camera to given angles x and y"""

        if abs(x) > 90:
            raise self.RangeWarning, "X parameter out of range"

        
        if abs(y) > 90:
            raise self.RangeWarning, "Y parameter out of range"

        #Convert from degrees to VISCA Parameter
        tmpx = (x * 862) / 90        
        if x < 0:
            tmpx = "0x" + hex(tmpx)[-4:]
        else:
            tmpx = hex(tmpx+1)

        tmpy = (y * 300) / 30
        if y < 0:
            tmpy = "0x" + hex(tmpy)[-4:]
        else:
            tmpy = hex(tmpy)

        tmpx = self._toParm(tmpx,4)
        tmpy = self._toParm(tmpy,4)

        command = struct.pack('B',0x02)

        command_message = command + self._panSpeed + self._tiltSpeed + tmpx + tmpy

        tmp = self._send_move(command_message)

        return self._ParseReturn(tmp)
        
            
    def getZoom(self):
        self._read()
        command = struct.pack('B',0x47)
        line = self._send_cam_inq(command)

        line = line[2:-1]
        line = self._convert_position(line)
        
        return line/1023.0


    def setZoom(self,Zoom):
        if not ((Zoom <= 1.0) and (Zoom >= 0)):
            raise self.RangeWarning, "Zoom out of Range"
        # zoom range: 0x0000 -> 0x03FF

        command = struct.pack('B',0x47)

        #convert float to VISCA zoom parameter
        tmpz = int(Zoom * 0x1FF)
        tmpz = "0x" + str(tmpz)
        tmpz = self._toParm(tmpz,4)

        command_message = command + tmpz
        line = self._send_cam(command_message)

        #wait for command completion
        self.sport.setTimeout(6)
        tmp = self.sport.read(3)
        self.sport.setTimeout(0.1)
        
        self.setSpeed(self._getSpeedFromZoom())
        return self._ParseReturn(line)


    def setPanSpeed(self,Speed):
        if not ((Speed <= 1.0) and (Speed >= 0)):
            raise self.RangeWarning, "Speed out of Range"
        if Speed == 0:
            self._panSpeed=struct.pack('B',1)
        else:
            self._panSpeed = struct.pack('B',(int(Speed * 23)))

    def getPanSpeed(self):
        return self._panSpeed


    def setTiltSpeed(self,(Speed)):
        if not ((Speed <= 1.0) and (Speed >= 0)):
            raise self.RangeWarning, "Speed out of Range"
        if Speed == 0:
            self._tiltSpeed=struct.pack('B',1)
        else:
            self._tiltSpeed = struct.pack('B',int(Speed * 20))

    def getTiltSpeed(self):
        return struct.unpack('B',self._tiltSpeed)[0]


    def getSpeed(self):
        return struct.unpack('B',self._panSpeed)[0]

    def setSpeed(self,speed):
        self.setPanSpeed(speed)
        self.setTiltSpeed(speed)

    #verb commands

    def PanLeftStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x01,0x03)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)

    def PanRightStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x02,0x03)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)

    def TiltUpStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x03,0x01)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)

    def TiltDownStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x03,0x02)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)

    
    def PanTiltStop(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x03,0x03)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)

    # convenience for diagonal motion

    def PanLeftTiltUpStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x01,0x01)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)
    
    def PanRightTiltUpStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x02,0x01)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)
        
    def PanLeftTiltDownStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x01,0x02)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)
        
    def PanRightTiltDownStart(self):
        command = struct.pack('B',0x01)
        parameter = struct.pack('2B',0x02,0x02)
        command_message = command + self._panSpeed + self._tiltSpeed + parameter
        return self._send_movec(command_message)



    # Zoom

    def ZoomInStart(self):
        command = struct.pack('2B',0x07,0x02)
        self._send_cam(command)
    
    def ZoomOutStart(self):
        command = struct.pack('2B',0x07,0x03)
        self._send_cam(command)
    
    def ZoomStop(self):
        command = struct.pack('2B',0x07,0x00)
        line = self._send_cam(command)
        
        # set pan/tilt speed
        self.setSpeed(self._getSpeedFromZoom())
        return self._ParseReturn(line)

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
        # This could actually be done directly as the visca protocl
        # defines a move relative command:
        # 'header, mode_move, category_cont, pan speed, tilt speed,
        # relative position x(4bytes), relative position y (4bytes)'

        # FIXME: Use VISCA relative movement commands
        
        tmp = self.getPosition()
        cPan, cTilt = tmp[0], tmp[1]
        self.setPosition( (cPan + Pan, cTilt + Tilt) )


    # Zoom
    def ZoomIn(self):
        # Set zoom doesn't work robustly
        # and the sony reference software never uses it.
        # so we just zoom a bit then stop.
        self.ZoomInStart()
        time.sleep(0.75)
        self.ZoomStop()
        
    def ZoomOut(self):
        self.ZoomOutStart()
        time.sleep(0.75)
        self.ZoomStop()
        
                
    #Home
    def MoveHome(self):
        """Move the camera to (0,0)"""
        command = struct.pack('B',0x04)
        return self._ParseReturn(self._send_move(command))

        
    # private methods


    def _convert_position(self,x):
        """turn a struct from the serial port to an integer"""
        x = struct.unpack('4b',x)
        
        ## account for negative 16 bit bit-patterns!
        tmp = ''
        for i in range(0,4):
            tmp = tmp +  hex(x[i])[2]
                        
        tmp = int(tmp,16)
        tmp = (tmp & 32767) - (tmp  & 32768)
        return tmp

    def _ParseReturn(self,line):
        if line is not None:
            hex_line = map( hex,struct.unpack(str(len(line))+'B',line))
            if 0x02 in hex_line:
                return "Syntax Error"
            if 0x03 in hex_line:
                return "Command Buffer Full"
            if 0x04 in hex_line:
                return "Command Cancel"
            if 0x05 in hex_line:
                return "No Sockets"
            if '0x41' in hex_line and '0x60' in hex_line:
                return "Command Not Executable"
            return None
        else:
            return None
        
    def _read(self):
        return self.sport.read(30) + self.sport.read(30)

    def _send(self,cmd):
        """Send a command over the serial port"""

        # cmd contains the command and parameter for a VISCA device
        # as the commands and parameters vary a lot accross the protocol
        # and will be set in the command
        self.sport.write(
            self._header +
            cmd +
            self._terminator)

        line = self._read()
        return line


    def _send_movec(self,cmd):
        "Continuos Movement (Pedastal) command (Left, Right, speeds etc)"
        self.sport.write(
            self._header +
            self._mode_control +
            self._category_move +
            cmd +
            self._terminator)
        tmp = self._read()
        
        #wait for ack
        self.sport.setTimeout(0.3)
        tmp = self.sport.read(3)
        self.sport.setTimeout(0.1)
        tmp = self._read()
        return self._ParseReturn(tmp)



    def _send_move(self,cmd):
        "Movement (Pedastal) command (Left, Right, speeds etc)"
        
        self.sport.write(
            self._header +
            self._mode_control +
            self._category_move +
            cmd +
            self._terminator)
        tmp = self._read()
        #wait for ack
        self.sport.setTimeout(None)
        self.sport.read(3)
        self.sport.setTimeout(0.1)
        return tmp

    def _send_cam(self,cmd):
        "Camera command, (Zoom,AE,Focus etc)"
        self.sport.write(
            self._header +
            self._mode_control +
            self._category_cam +
            cmd +
            self._terminator)


        tmp = self._header +self._mode_control + self._category_cam + cmd + self._terminator

        return self._ParseReturn(self._read())


    def _send_cam_inq(self,cmd):
        "Camera Inquiry"
        self.sport.write(
            self._header +
            self._mode_info +
            self._category_cam +
            cmd +
            self._terminator)
        return self._read()


    def _send_move_inq(self,cmd):
        "Pedastal inquiry"
        self.sport.write(
            self._header +
            self._mode_info +
            self._category_move +
            cmd +
            self._terminator)
        return self._read()

    def _send_request(self,cmd):
        """Send an Information Request command over the serial port"""
        self.sport.write(
            self._header +
            cmd +
            self._terminator)
        
        line = self._read()
        return line

            
    def _getSpeedFromZoom(self):
        #print "DEBUG: Zoom =", Zoom
        speed = (1.0-self.getZoom())/2.0
        #print "DEBUG: Speed=", speed
        return speed


    def _getQuantaFromZoom(self):
        Zoom = self.getZoom()
        if Zoom == 1.0:
            #adjust for boundary
            movement_quanta = 1
        else:
            movement_quanta = 5 - (5*Zoom)
        return movement_quanta

    def _toParm(self,parameter,size):
        """Returns the VCC control Code for the integer 'parameter'
        eg, parameter = 9, result=0x30,0x35"""
        tmp=[]
        hex_string = parameter
        hex_string = hex_string[hex_string.find('x')+1:]
        
        if len(hex_string) < size:
            for i in range (0,size-(len(hex_string))):
                hex_string = '0' + hex_string
    
            
        for i in range(0,size):
            tmp.append( int(hex_string[i],16))
        return_string = ''
        for i in range(0,size):
            return_string = return_string + struct.pack('B',tmp[i])
        return return_string
