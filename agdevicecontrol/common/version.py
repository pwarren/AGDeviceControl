#!/usr/bin/env python
# -*- test-case-name: agdevicecontrol.test.test_version -*-
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

#------------------
major = 0
minor = 5
incremental = 4
#------------------


# join above in major.minor.incremental format (e.g., 0.9.8)
version = '.'.join( map(str, [major, minor, incremental]) )

# api changes are signified by jump in the minor version ...
apiversion = '.'.join( map(str, [major, minor]) )


def fromString(s):
    """Extract version components (major,minor,incremental) from a string"""

    # "Some people, when confronted with a problem, think 'I know,
    #  I'll use regular expressions.' Now they have two problems."
    #     -- Jamie Zawinski, on comp.lang.emacs
    import re

    # 0.0.0 format
    pattern = re.compile( "(?P<major>[0-9]+)\.(?P<minor>[0-9])\.(?P<incremental>[0-9]+)" )
    match = pattern.search(s)
    if match:
        major = int(match.group('major'))
        minor = int(match.group('minor'))
        incremental = int(match.group('incremental'))
        return (major,minor,incremental)

    # older 0.00 format
    pattern = re.compile( "(?P<major>[0-9]+)\.(?P<minor>[0-9])(?P<incremental>[0-9])" )
    match = pattern.search(s)
    if match:
        major = int(match.group('major'))
        minor = int(match.group('minor'))
        incremental = int(match.group('incremental'))
        return (major,minor,incremental)

    # doesn't appear to be a version string
    raise ValueError, 'Could not extract (major,minor,incremental) from "%s"' % s



def hasExpired(client,server):
    """Check if server is 'significantly' newer than client (ie., not just an incremental change)"""

    client_version = fromString(client)
    server_version = fromString(server)

    # exact match
    if client_version == server_version:
        return False

    # tuple unpacking
    (cmajor,cminor,cincremental) = client_version
    (smajor,sminor,sincremental) = server_version

    # sanity checks, client is newer than server???
    if cmajor > smajor:
        raise VersionError, 'Client %s is newer than Server %s' % (client_version,server_version)
    if cmajor == smajor and cminor > sminor:
        raise VersionError, 'Client %s is newer than Server %s' % (client_version,server_version)

    # mismatch in minor or major versions
    if cmajor != smajor or cminor != sminor:
        return True

    # incremental change
    raise VersionWarning, 'Client %s is slightly out of date from Server %s, upgrade recommended' \
          % (client_version,server_version)


def toFloat(version_string):
    """AGTk Node Services require version as a floating point value, x.y.z, causes problems"""

    version = fromString(version_string)
    return float("%s.%s%s" % version)



class VersionWarning(Exception):
    pass


class VersionError(Exception):
    pass

