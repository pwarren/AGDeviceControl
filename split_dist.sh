#!/bin/bash

VERSION=$1

# run a shell script to split into os dependant versions.

gunzip dist/agdevicecontrol-$VERSION.tar.gz

## win32
cp dist/agdevicecontrol-$VERSION.tar dist/agdevicecontrol-win32-$VERSION.tar

tar -f dist/agdevicecontrol-win32-$VERSION.tar --delete agdevicecontrol-$VERSION/agdevicecontrol/thirdparty/site-packages/linux2

tar -f dist/agdevicecontrol-win32-$VERSION.tar --delete agdevicecontrol-$VERSION/agdevicecontrol/thirdparty/site-packages/darwin

gzip -f dist/agdevicecontrol-win32-$VERSION.tar


## linux2
cp dist/agdevicecontrol-$VERSION.tar dist/agdevicecontrol-linux-$VERSION.tar

tar -f dist/agdevicecontrol-linux-$VERSION.tar --delete agdevicecontrol-$VERSION/agdevicecontrol/thirdparty/site-packages/win32

tar -f dist/agdevicecontrol-linux-$VERSION.tar --delete agdevicecontrol-$VERSION/agdevicecontrol/thirdparty/site-packages/darwin

gzip -f dist/agdevicecontrol-linux-$VERSION.tar


## Darwin
cp dist/agdevicecontrol-$VERSION.tar dist/agdevicecontrol-darwin-$VERSION.tar

tar -f dist/agdevicecontrol-darwin-$VERSION.tar --delete agdevicecontrol-$VERSION/agdevicecontrol/thirdparty/site-packages/win32

tar -f dist/agdevicecontrol-darwin-$VERSION.tar --delete agdevicecontrol-$VERSION/agdevicecontrol/thirdparty/site-packages/linux2

gzip -f dist/agdevicecontrol-darwin-$VERSION.tar
