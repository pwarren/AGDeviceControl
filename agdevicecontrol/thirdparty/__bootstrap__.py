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


"""
Rather than require users to install dependencies such as ZopeInterfaces
and Twisted, we include them as part of the AGDeviceControl distribution.
The problem is that dependencies may or may not have platform-specific
code.  Bootstrap adjusts the python (import) path to refer to the
appropriate platform-specific code.  __bootstrap__ was contributed
by Bob Ippolito in response to a question on the Twisted maillist.
"""

import os, sys

# store startup directory
stored_dir = os.getcwd()

# change to current directory
curdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curdir)

# add dependencies and platform specific path for dependencies
sitepkg = os.path.join(curdir, 'site-packages')

# one of 'darwin', 'linux' or 'win32' 
platdir = sys.platform.lower()

# modify module search path
sys.path.insert(1, os.path.join(sitepkg, platdir))

#print "**********************************************************************"
#print sys.path
#print "**********************************************************************"

# restore to initial directory
os.chdir(stored_dir)
