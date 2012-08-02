#!/usr/bin/env python

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

from distutils.core import setup
import glob
import os
import sys
import re


def get_data_files():
    """hack for no package_data in python2.3 distutils"""
    data = []
    if sys.platform  == "win32":
        dot = re.compile('.*' + os.path.sep + '..*')
    else:
        dot = re.compile('.*' + os.path.sep + '\..*')
    dl = ""
    for d in os.walk(os.path.join("agdevicecontrol","gui","images")):
        if not os.path.basename(d[0]).startswith(".") and not dot.match(d[0]):
            for f in d[2]:
                if not f.startswith("."):
                    if sys.platform == "win32":
                        dl = os.path.join("","lib","site-packages",d[0])  # destination
                    else:
                        dl = os.path.join("","lib","python" + sys.version[:3],"site-packages",d[0])
                    data.append((dl, [os.path.join(d[0], f)]))
    return data
                


twisted_packages = ["application",
                    "cred",
                    "persisted",
                    "protocols",
                    "spread",
                    "trial",
                    "enterprise",
                    "internet",
                    "python",
                    "tap",
                    "manhole",
                    "plugins",
                    "scripts"]

zope_packages = ["interface"]


p = ["agdevicecontrol",
     "agdevicecontrol.common","agdevicecontrol.common.seqdict",
     "agdevicecontrol.common.seqdict.hide",
     "agdevicecontrol.clients",
     "agdevicecontrol.multicast",
     "agdevicecontrol.devices",
     "agdevicecontrol.gui",
     "agdevicecontrol.server",
     "agdevicecontrol.thirdparty",
     ]

p.append("agdevicecontrol.thirdparty.site-packages." + sys.platform + ".twisted")

for package in twisted_packages:
    p.append("agdevicecontrol.thirdparty.site-packages." + sys.platform + ".twisted." + package)
    
p.append("agdevicecontrol.thirdparty.site-packages." + sys.platform + ".zope")
for package in zope_packages:
    p.append("agdevicecontrol.thirdparty.site-packages." + sys.platform + ".zope." + package)

p.append("agdevicecontrol.thirdparty.site-packages." +sys.platform + ".serial")


s = ["agdevicecontrol/bin/server.py",
     "agdevicecontrol/bin/visca-test.py",
     "agdevicecontrol/bin/vcc4-test.py",     
     "agdevicecontrol/thirdparty/site-packages/" + sys.platform + "/twisted/bin/twistd"]

for x in p:
    print x

if __name__ == "__main__":

    setup(name = "agdevicecontrol",
          version = "0.5.4",
          description = "AGDeviceControl",
          author = "Paul Warren and Darran Edmundson",
          author_email = "ag@anusf.anu.edu.au",
          url = "http://agcentral.org/downloads/agdevicecontrol",
          packages = p,
          scripts = s,
          data_files = get_data_files(),
          classifiers = ['License :: OSI Approved :: GNU General Public License',
                         'Operating System :: MacOS :: MacOS X',
                         'Operating System :: Microsoft :: Windows',
                         'Operating System :: POSIX']
          )
