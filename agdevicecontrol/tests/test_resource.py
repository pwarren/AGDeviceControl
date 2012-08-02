
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


import os.path
from glob import glob as pyglob

import agdevicecontrol
import agdevicecontrol.common.resource as resource
from twisted.trial import unittest


class TestResource(unittest.TestCase):

    def test_globdict(self):
        """Dictionary of fully qualified paths keyed by filename for package directory"""

        base_path = agdevicecontrol.__path__[0]

        # fully qualified paths to images
        fqfiles = map(os.path.abspath, pyglob(base_path + "/gui/images/*.png"))
        fqfiles.sort()
        
        dict = resource.globdict("agdevicecontrol.gui", subdir="images", filter='*.png')

        assert len(dict) == len(fqfiles)
        for fqfile in fqfiles:
            file = os.path.split(fqfile)[1]
            assert file in dict
            assert dict[file] == fqfile


    def test_subpackage(self):
        """Fully qualified path of subpackage"""
        base_path = agdevicecontrol.__path__[0]
        path = os.path.abspath(base_path + '/server')
        f = resource.module_path('agdevicecontrol.server')
        assert f == path


    def test_module(self):
        """Fully qualified path of package module file"""
        base_path = agdevicecontrol.__path__[0]
        path = os.path.abspath(base_path + '/clients/connector.pyc')
        f = resource.module_path('agdevicecontrol.clients.connector')
        assert f == path

