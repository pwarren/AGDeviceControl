#!/usr/bin/env python

# NodeServices are stored as a zip archive.  Contains the
# script that interacts with the external app and a .svc
# config file + the external app itself.  NodeServices are
# installed by the AG Package Manager (agpm.py).

import agdevicecontrol
from agdevicecontrol.common.version import version, toFloat

f = open("DeviceControlService.svc",'w')
f.write("""
[ServiceDescription]
name = DeviceControlService
description = Remote Control of AG Hardware Resources
capabilities = Capability1
executable = DeviceControlService.py
platform = neutral
version = %4.2f

[Capability1]
role = producer
type = agdevicecontrol
""" % toFloat(version))
f.close()



from zipfile import ZipFile
import os, os.path

manifest = [
    "DeviceControlService.py",
    "DeviceControlService.svc",
    "main.py",
    "aggregator.conf"
    ]

# needs to run from script directory
archive_file = os.path.join('..', '..', 'DeviceControlService.zip')

if os.path.isfile(archive_file):
    os.remove(archive_file)

archive = ZipFile(archive_file, 'w')
for f in manifest:
    archive.write(f)
archive.close()


# cleanup
os.remove("DeviceControlService.svc")
