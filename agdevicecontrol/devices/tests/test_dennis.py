
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
from dennis import Dennis
from vehicle import VehicleException
import py
import types

def setup_module(module):
    global dns
    dns = Dennis(phid=5927)

def teardown_modules(module):
    pass
    

class TestDennis:

    disabled = 0
    
    def test_forward(self):
        dns.forward()
        sleep(0.25)
        dns.stop()

    def test_reverse(self):
        dns.reverse()
        sleep(0.25)
        dns.stop()

    def test_spin_left(self):
        dns.spinLeft()
        sleep(0.25)
        dns.spinStop()

    def test_spin_right(self):
        dns.spinRight()
        sleep(0.25)
        dns.spinStop()

    def test_speed_up(self):
        dns.forward()
        sleep(0.25)
        dns.speedUp()
        sleep(0.25)
        dns.stop()

    def test_slow_down(self):
        dns.forward()
        sleep(0.25)
        dns.slowDown()
        sleep(0.25)
        dns.stop()

    def test_turn_left(self):
        dns.forward()
        sleep(0.25)
        dns.turnLeft()
        sleep(0.25)
        dns.stop()

    def test_turn_right(self):
        dns.forward()
        sleep(0.25)
        dns.turnRight()
        sleep(0.25)
        dns.stop()

    def test_no_dennis(self):
        py.test.raises(VehicleException, "Dennis(phid=9999)")

