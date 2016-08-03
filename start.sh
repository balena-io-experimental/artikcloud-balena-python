#!/usr/bin/bash

# ARTIKCLOUD_CONNECTION defines the default protocol to talk to ARTIk Cloud,
# and results in running different code within the app.
# Possible values: mqtt, websockets
# Default value: mqtt
case "${ARTIKCLOUD_CONNECTION=mqtt}" in
  mqtt)
    echo "Starting MQTT version"
    ;;
  websockets)
    echo "Starting WebSockets version"
    ;;
  *)
    echo "Uknown ARTIKCLOUD_CONNECTION value: ${ARTIKCLOUD_CONNECTION}"
    echo "Should be one of: mqtt, websockets"
    while : ; do echo "idling..."; sleep 60; done
    ;;
esac

APP_FILENAME="device_${ARTIKCLOUD_CONNECTION}.py"

python "artik/$APP_FILENAME"
