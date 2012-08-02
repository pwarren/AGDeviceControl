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
from agdevicecontrol.devices.switch import ISwitch
from agdevicecontrol.devices.device import Device
from agdevicecontrol.common.abstract import abstract
from zope.interface import implements, Interface



class ICamera(ISwitch):
    """Generic PTZ interface (inheriting power on/off interface)"""


    # PTZ absolute positioning commands

    def getPosition():
        """Camera position as a (pan,tilt) tuple in degrees with (0,0) being forward looking"""

    def setPosition(position):
        """Camera position as a (pan,tilt) tuple in degrees with (0,0) being forward looking"""

    def getZoom():
        """Camera zoom as float 0-1 (wide-tight)"""

    def setZoom(zoom):
        """Camera zoom as float 0-1 (wide-tight)"""


    # Discrete PTZ commands (suggest making the PT movements smaller when zoomed tight, larger when zoomed out)

    def PanLeft():
        """Rotate camera head left by finite amount commensurate with the current zoom level"""
    
    def PanRight():
        """Rotate camera head right by finite amount commensurate with the current zoom level"""
    
    def TiltUp():
        """Rotate camera head upwards by finite amount commensurate with the current zoom level"""
    
    def TiltDown():
        """Rotate camera head downwards by finite amount commensurate with the current zoom level"""
    
    def PanLeftTiltUp():
        """Rotate camera head diagonal left and up by finite amount commensurate with the current zoom level"""

    def PanRightTiltUp():
        """Rotate camera head diagonal right and up by finite amount commensurate with the current zoom level"""
        
    def PanLeftTiltDown():
        """Rotate camera head diagonal left and down by finite amount commensurate with the current zoom level"""

    def PanRightTiltDown():
        """Rotate camera head diagonal right and down by finite amount commensurate with the current zoom level"""

    def ZoomIn():
        """Zoom tighter by small finite amount"""
    
    def ZoomOut():
        """Zoom wider by small finite amount"""

    def MoveHome():
        """Move to (0,0)"""



    # PTZ open-ended motion commands (commands require an associated Stop to end action)

    def PanLeftStart():
        """Begin rotating camera head left"""
    
    def PanRightStart():
        """Begin rotating camera head right"""
    
    def TiltUpStart():
        """Begin rotating camera head upwards"""
    
    def TiltDownStart():
        """Begin rotating camera head downwards"""
    
    def PanLeftTiltUpStart():
        """Begin rotating camera head diagonal left and up"""

    def PanRightTiltUpStart():
        """Begin rotating camera head diagonal right and up"""
        
    def PanLeftTiltDownStart():
        """Begin rotating camera head diagonal left and down"""

    def PanRightTiltDownStart():
        """Begin rotating camera head diagonal right and down"""

    def PanTiltStop():
        """Cease any ongoing movement"""

    def ZoomInStart():
        """Begin zooming tighter"""
    
    def ZoomOutStart():
        """Begin zooming wider"""
    
    def ZoomStop():
        """Cease any ongoing zoom"""




class Camera(Device):
    """Camera Abstract Class"""

    implements(ICamera)

    def getDeviceType(self):
        return "Camera"



    class CameraException(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    class ModeWarning(CameraException):
        pass
    
