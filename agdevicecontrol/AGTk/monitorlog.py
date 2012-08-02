#!/bin/env python

# convenience script to monitor the log relating to
# our budding service.  Useful for debugging

import sys
import os

if sys.platform == 'darwin':
    logdir = '~/.AccessGrid/Logs'
    logfile = 'DeviceControlService.log'


cmd = "tail -f %s/%s" % (logdir,logfile)
os.system(cmd)

