#!/usr/bin/env python

import os
import agdevicecontrol
import agdevicecontrol.common.version as version

start_dir = os.getcwd()

os.chdir('agdevicecontrol'+os.sep+'AGTk')
os.system('python makepackage.py')
os.chdir(start_dir)
os.system('python setup.py sdist')
os.system('sh ./split_dist.sh ' + version.version)
os.system('python setup.py bdist_wininst')
