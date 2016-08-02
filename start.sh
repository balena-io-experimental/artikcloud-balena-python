#!/usr/bin/bash

# ARTIKCLOUD_CONNECTION defines the default protocol to talk to ARTIk Cloud,
# and results in running different code within the app.
# Possible values: rest, sdk, mqtt, websockets
# Default value: mqtt
APP_FILENAME="device_${ARTIKCLOUD_CONNECTION-mqtt}.py"

python "artik/$APP_FILENAME"
