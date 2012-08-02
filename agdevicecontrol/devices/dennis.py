
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


from vehicle import Vehicle, VehicleException

try:
    import phidgets
    from phidgets.quadservo import phidget_new_PhidgetQuadServo as quadservo_id
    from phidgets.quadservo import phidget_quadservo_set_servo_parameters as quadservo_parameters
    from phidgets.quadservo import phidget_quadservo_open as quadservo_open
    from phidgets.quadservo import phidget_quadservo_set_all_positions as quadservo_positions
    from phidgets.quadservo import phidget_quadservo_set_all_positions as quadservo_position_all
    from phidgets.quadservo import phidget_quadservo_set_single_position as quadservo_position_single
    from phidgets.quadservo import PHIDGET_QUADSERVO_MOTOR0, PHIDGET_QUADSERVO_MOTOR1, PHIDGET_QUADSERVO_MOTOR2, PHIDGET_QUADSERVO_MOTOR3
except ImportError:
    raise VehicleException, "Couldn't import Phidget modules"

import sys
import time


# must be done once when using phidgets
if phidgets.phidget_init():
    raise VehicleException, "Couldn't initialize Phidget library"


def convert(x):
    """Utility method for converting between float and phidget-required longint"""
    return int(x*sys.maxint)


#----------------------------------------------------------------------
class QuadServo:
    """Thin wrapper around quad servo C library"""

    def __init__(self, phid, retries=3):

        self.phid = phid
        self.qsid = quadservo_id()
        quadservo_open(self.qsid, self.phid, retries)


    def setRange(self, n, minval, maxval):
        """Servo has adjustable min, max positions (and final 10.6 'factor' though no idea what this does)"""
        quadservo_parameters(self.qsid, n, minval, maxval, 10.6)


    def setPositionAll(self, positions):
        p0, p1, p2, p3 = tuple( [convert(i) for i in positions] )
        quadservo_position_all( self.qsid, p0, p1, p2, p3 )

    def setPositionSingle(self, servo, position):
        quadservo_position_single( self.qsid, servo, convert(position) )



#----------------------------------------------------------------------
class Dennis(Vehicle):
    """Dennis, a controllable tracked-vehicle platform

    Dennis is a toy 1/16th scale toy remote-control tank stripped
    down to the tread chassis with the RF control replaced by a USB
    controlled QuadServo Phidget.  Dennis is named after Dennis
    Gibson, the electronics technician at The Australian National
    University RSPhysSE Electronics shop who suggested Phidgets
    and rewired the guts of the tank.  He had no say in the matter.
    """
           
    def __init__(self, *args, **kwargs):

        Vehicle.__init__(self, *args, **kwargs)

        # quad servo controller
        if hasattr(self,'phid'):
            self.phid = int(self.phid)
        else:
            self.phid = 5927
        self.q = QuadServo( self.phid )

        # each servo has adjustable min, max positions (and final 10.6 "factor" - no idea what this does)
        self.q.setRange( PHIDGET_QUADSERVO_MOTOR0, 100, 3000 )
        self.q.setRange( PHIDGET_QUADSERVO_MOTOR1, 1000, 3000 )
        self.q.setRange( PHIDGET_QUADSERVO_MOTOR2, 1000, 3000 )

        # servo motor controller positions, the middle 0.5 is stopped
        self.rest = 0.5
        self.forward_start = 0.54
        self.spin_forward_start = 0.54
        self.motion_delta = 0.02
        self.turn_delta = 0.01
        self.spin_delta = 0.01
        self.reverse_start = 0.45
        self.spin_reverse_start = 0.46
        self.max = 0.70
        self.min = 0.30
        self.tilt_min = 0.25
        self.tilt_max = 0.85
        self.tilt_delta = 0.01

        self.left = self.rest
        self.right = self.rest
        self.tilt = 0.5

        self.left_previous = self.left
        self.right_previous = self.right
        self.tilt_previous = self.tilt

        self.state = 'STOPPED'


    def forward(self):
        if not self.state == 'FORWARD':
            self.left = self.forward_start
            self.right = self.forward_start
            self.state = 'FORWARD'
            self._update()


    def reverse(self):
        if not self.state == 'REVERSE':
            self.left = self.reverse_start
            self.right = self.reverse_start
            self._update()

            self.left = self.rest + self.motion_delta
            self.right = self.rest + self.motion_delta
            self._update()

            self.left = self.reverse_start
            self.right = self.reverse_start
            self._update()
            
            self.state = 'REVERSE'


    def stop(self):
        self.left = self.rest
        self.right = self.rest
        self.state = 'STOPPED'
        self._update()


    def turnLeft(self):
        self.left -= self.turn_delta
        self.right += self.turn_delta
        self._update()

    def turnRight(self):
        self.left += self.turn_delta
        self.right -= self.turn_delta
        self._update()


    def speedUp(self):
        if self.state == "FORWARD":
            self.left += self.motion_delta
            self.right += self.motion_delta
        else:
            self.left -= self.motion_delta
            self.right -= self.motion_delta
        self._update()


    def slowDown(self):
        if self.state == "FORWARD":
            self.left -= self.motion_delta
            self.right -= self.motion_delta
        else:
            self.left += self.motion_delta
            self.right += self.motion_delta
        self._update()

        
    def spinLeft(self):
        if not self.state == "SPINNING":
            self._reverse(PHIDGET_QUADSERVO_MOTOR1)
            self.left = self.spin_reverse_start
            self.right = self.spin_forward_start
            self._spinupdate()
            self.state = "SPINNING"
        else:
            self.left -= self.spin_delta
            self.right += self.spin_delta
            self._spinupdate()
            
 
    def spinRight(self):
        if not self.state == "SPINNING":
            self._reverse(PHIDGET_QUADSERVO_MOTOR2)
            self.right = self.spin_reverse_start
            self.left = self.spin_forward_start
            self._spinupdate()
            self.state = "SPINNING"
        else:
            self.left += self.spin_delta
            self.right -= self.spin_delta
            self._spinupdate()


    def spinStop(self):
        self.stop()
        time.sleep(0.1)
        

    def tiltUp(self):
        self.tilt += self.tilt_delta
        if self.tilt > self.tilt_max:
            self.tilt = self.tilt_max
        self.q.setPositionSingle(PHIDGET_QUADSERVO_MOTOR0,self.tilt)
        time.sleep(0.1)


    def tiltDown(self):
        self.tilt -= self.tilt_delta
        if self.tilt < self.tilt_min:
            self.tilt = self.tilt_min
        self.q.setPositionSingle(PHIDGET_QUADSERVO_MOTOR0,self.tilt)
        time.sleep(0.1)


    def _reverse(self,servo):
        self.q.setPositionSingle(servo,self.reverse_start)
        time.sleep(0.1)
        self.q.setPositionSingle(servo,self.rest)
        time.sleep(0.1)
        

    def _spinupdate(self):

        if self.left < self.rest:
            if self.left_previous > self.rest:  # just reversed (crossed middle threshold)
                self._reverse(PHIDGET_QUADSERVO_MOTOR1)
                self.left = self.reverse_start
            elif self.left < self.min:
                self.left = self.min
        elif self.left > self.max:
            self.left = self.max

        if self.right < self.rest:
            if self.right_previous > self.rest:  # just reversed (crossed middle threshold)
                self._reverse(PHIDGET_QUADSERVO_MOTOR2)
                self.right = self.reverse_start
            elif self.right < self.min:
                self.right = self.min
        elif self.right > self.max:
            self.right = self.max

        self.q.setPositionAll( [self.tilt, self.left, self.right, 0] )

        self.left_previous = self.left
        self.right_previous = self.right



    def _update(self):

        if self.state == "FORWARD":
            if self.left < self.rest:            
                self.left = self.rest
            elif self.left > self.max:
                self.left = self.max

            if self.right < self.rest:            
                self.right = self.rest
            elif self.right > self.max:
                self.right = self.max

        elif self.state == "REVERSE":
            if self.left > self.rest:            
                self.left = self.rest
            elif self.left < self.min:
                self.left = self.min

            if self.right > self.rest:            
                self.right = self.rest
            elif self.right < self.min:
                self.right = self.min

        #print "%s\tleft %f\tright %f" % (self.state, self.left, self.right)
        self.q.setPositionAll( [self.tilt, self.left, self.right, 0] )

        self.left_previous = self.left
        self.right_previous = self.right
        self.tilt_previous = self.tilt



#----------------------------------------------------------------------
if __name__ == "__main__":
    d = Dennis()
    d.forward()
    time.sleep(1)
    for i in range(20):
        d.tiltUp()
        time.sleep(0.1)
    d.stop()
