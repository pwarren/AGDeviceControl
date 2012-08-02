#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_resource -*-
#
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


from glob import glob as pyglob
import imp
import os, os.path


def module_path(p, path=None):
    """Recursive search to find a module's absolute path"""

    # package hierarchy is dot separated, e.g., agdevicecontrol.clients
    components = p.split('.')

    modname = components[0]
    
    file, path, description = imp.find_module(modname,path)
    if file is not None:
        try:
            modobj = imp.load_module(modname, file, path, description)
            #print "DEBUG: ", modobj.__file__
            path = modobj.__file__
        finally:
            file.close()

    if len(components) == 1:
        return path
    else:
        return module_path('.'.join(components[1:]), path=[path])
    
    

def globdict(package, subdir=[], filter='*'):

    # find absolute file path of package
    path = module_path(package)

    # add subdirs
    path += os.sep + os.path.join(subdir)

    if os.path.isdir(path):
        dict = {}
        for f in pyglob(path + os.sep + filter):
            dict[os.path.split(f)[1]] = f
        return dict
    else:
        raise ImportError

