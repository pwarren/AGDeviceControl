
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


from time import sleep
from vcc4 import VCC4
import py
import types

def setup_module(module):
    global cam
    cam = VCC4(port=0,daisychain=0)
    cam._startup()


def teardown_modules(module):
    cam.hostControlMode()
    
class TestVCC4:

    disabled = 0
    
    def test_pan_left(self):
        assert cam.PanLeft() is None
        sleep(1)
        assert cam.PanTiltStop() is None

    def test_pan_right(self):
        assert cam.PanRight() is None
        sleep(1)
        assert cam.PanTiltStop() is None

    def test_tilt_down(self):
        assert cam.TiltDown() is None
        sleep(0.25)
        assert cam.PanTiltStop() is None

    def test_tilt_up(self):
        assert cam.TiltUp() is None
        sleep(0.25)
        assert cam.PanTiltStop() is None


    def test_zoom_in(self):
        assert cam.ZoomIn() is None
        sleep(1)
        assert cam.ZoomStop() is None

    def test_zoom_out(self):
        assert cam.ZoomOut() is None
        sleep(1)
        assert cam.ZoomStop() is None

    def test_set_zoom_value1(self):
        assert cam.setZoom(0.5) is None
        sleep(2)
        assert cam.getZoom() == 0.5

    def test_set_zoom_value2(self):
        assert cam.setZoom(0.1) is None
        sleep(2)
        assert (cam.getZoom() - 0.1) <= 0.01

    def test_set_zoom_max(self):
        assert cam.setZoom(1) is None
        sleep(4)
        assert cam.getZoom() == 1.0

    def test_set_zoom_min(self):
        assert cam.setZoom(0) is None
        sleep(4)
        assert cam.getZoom() == 0.0

    def test_zoom_above_max_value(self):
        py.test.raises(cam.RangeWarning, cam.setZoom, 1000)

    def test_zoom_below_min_value(self):
        py.test.raises(cam.RangeWarning, cam.setZoom, -10)


    def test_power_off(self):
        assert cam.setPower('Off') is None
        assert cam.getPower() is 'Off'

    def test_power_on(self):
        assert cam.setPower('On') is None
        assert cam.getPower() is 'On'

    
    def test_get_known_position(self):
        assert cam.MoveHome() is None
        sleep(2)
        assert cam.getPosition() == (0,0)

    def test_set_position_home(self):
        assert cam.setPosition((0,0)) is None
        sleep(2)
        assert cam.getPosition() == (0,0)

    def test_set_position_quadrant1(self):
        assert cam.setPosition((-45,8)) is None
        sleep(2)
        assert cam.getPosition() == (-45,8)

    def test_set_position_quadrant2(self):
        assert cam.setPosition((30,1)) is None
        sleep(2)
        assert cam.getPosition() == (30,1)

    def test_set_position_quadrant3(self):
        assert cam.setPosition((-30,-1)) is None
        sleep(2)
        assert cam.getPosition() == (-30,-1)
        
    def test_set_position2(self):
        """Test that for VC-C4R setPosition works, and for VC-C4, it returns a range exception (128,8)"""
        if cam._CamTypeRequest() == 'VC-C4':
            py.test.raises(cam.RangeWarning, cam.setPosition, (128,8))
        else:
            cam.setPosition((128,8))
            sleep(2.5)
            assert cam.getPosition() == (128,8)
            
    def test_set_position3(self):
        if cam._CamTypeRequest() == 'VC-C4':
            py.test.raises(cam.RangeWarning, cam.setPosition, (128,-80))
        else:  # VC-C4R has larger range
            cam.setPosition((128,-80))
            sleep(2.5)
            assert cam.getPosition() == (128,-80)
                         
    def test_set_position_highx(self):
        sleep(2)
        py.test.raises(cam.RangeWarning, cam.setPosition, (1000,0))

    def test_set_position_highy(self):
        sleep(2)
        py.test.raises(cam.RangeWarning, cam.setPosition, (0,1000))


    def test_mode_warning(self):
        cam.setPower('Off')
        py.test.raises(cam.ModeWarning, cam.setPosition,(0,0))
        

    def test_name_mangle(self):
        cam.setPower(['On'])
        sleep(2.5)
        assert cam.getPower() == 'On'

    def test_command_gets_through_local_control_mode(self):
        
        cam.localControlMode()
        sleep(2)
        return_value = cam.getPosition()        
        assert type(return_value) == types.TupleType

    def test_Pan_speed1(self):
        cam.setPanSpeed(0.0)
        speed = cam.getPanSpeed()
        assert speed == 0.0

    def test_Pan_speed2(self):
        cam.setPanSpeed(1.0)
        speed = cam.getPanSpeed()
        assert speed == 1.0

    def test_Tilt_speed1(self):
        cam.setTiltSpeed(0.0)
        speed = cam.getTiltSpeed()
        assert speed == 0.0

    def test_Tilt_speed2(self):
        cam.setTiltSpeed(1.0)
        speed = cam.getTiltSpeed()
        assert speed == 1.0

    def test_quantised_movement1(self):
        cam.MoveHome()
        cam.setZoom(0.0)
        sleep(3.0)
        cam.PanLeft()
        sleep(0.3)
        result = cam.getPosition()
        assert result == (-10, 0)

    def test_quantised_movement2(self):
        cam.MoveHome()
        cam.setZoom(0.0)
        cam.TiltUp()
        sleep(0.3)
        result = cam.getPosition()
        assert result == (0, 10)

    def test_quantised_movement3(self):
        cam.MoveHome()
        cam.setZoom(1.0)
        sleep(3)
        print cam.movement_quanta
        cam.PanLeft()
        sleep(1.3)
        assert cam.getPosition() == (-1,0)
