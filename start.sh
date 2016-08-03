#!/usr/bin/bash

# ARTIKCLOUD_CONNECTION defines the default protocol to talk to ARTIk Cloud,
# and results in running different code within the app.
# Possible values: mqtt
# Default value: mqtt
case "${ARTIKCLOUD_CONNECTION=mqtt}" in
  mqtt)
    echo "Starting MQTT version"
    ;;
  *)
    echo "Uknown ARTIKCLOUD_CONNECTION value: ${ARTIKCLOUD_CONNECTION}"
    echo "Should be one of: mqtt"
    while : ; do echo "idling..."; sleep 60; done
    ;;
esac

APP_FILENAME="device_${ARTIKCLOUD_CONNECTION}.py"

python "artik/$APP_FILENAME"
