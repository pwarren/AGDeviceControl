#!/bin/sh

# Remove and reinstall the service.  Probably only works on Mac at the moment ...

# remove existing
python $AGTK_LOCATION/bin/agpm.py --unregister-service -n DeviceControlService.zip

# copy of the service in local directory, need to remove.  AGTk will copy this
# over when the service is requested.
rm -rf ~/.AccessGrid/local_services/DeviceControlService

# clear log
rm -rf ~/.AccessGrid/Logs/DeviceControlService.log

# reinstall
python $AGTK_LOCATION/bin/agpm.py --package=DeviceControlService.zip
