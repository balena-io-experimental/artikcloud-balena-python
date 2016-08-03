# ARTIK Cloud Device on resin.io

__/!\ Work in progress!__

Implementing a basic [ARTIK Cloud](https://artik.cloud) device with
resin.io. It exercises sending data and receiving actions using multiple
connection types (Websockets, MQTT at the moment).

The sensor side of the application implements 3 readings to create interesting
data streams that can be used for testing:

* CPU utilization
* Free memory
* Random number

The random number is a useful stream to probabilistically trigger an event on
the ARTIK Cloud.

The actions side of the application implements 3 typs of actions:

* `setText`: set a text value, here write to the log
* `setOff`: turn the device off using the Supervisor API
* `blinkLed`: blink the device identification LED (on those devices where
   it is available), using the SupervisorAPI

## ARTIK Cloud setup

A summarized/shortened version of setting up the ARTIK Cloud side of the deployment.

1. Create a device type with the appropriate [manifest](./manifest.json).
2. Create a device with the given device type
3. Get credentials from devices dashboard
4. Set up rules to trigger actions on the device (optional)

## Resin setup

A summarized/shortened version of setting up the resin.io side of the deployment.

1. Create a new application in the resin.io dashboard.
2. Deploy a new device
3. Set up environment variables (see below)
4. Push code to the application
5. Check log

## Environment variables

The used (software) environment variables to control the behaviour of the
application are the following:

* `ARTIKCLOUD_DEVICE_ID`: get it from your [ARTIK Cloud devices dashboard](https://artik.cloud/my/devices)
* `ARTIKCLOUD_DEVICE_TOKEN`: get it from your [ARTIK Cloud devices dashboard](https://artik.cloud/my/devices)
* `ARTIKCLOUD_CONNECTION`: which implementation to run. Implemented: mqtt (default), websockets
* `READINGS_PERIOD`: how often to take a reading, in seconds, default=600

## Setting up actions

Setting up actions can be done on the ARTIK Clpud [Rules dashboard](https://artik.cloud/my/rules).
There one can define conditions that trigger specific actions on specific devices.
It can be quite complex and powerful, so recommended to check it out.

Some example actions:

* when on "Any" device of the given device type the vale of "Random" is smaller
  than 0.05, send the `setOff` event to that "Any" device (1:20 chance to turn off the device)
* when on "All" device of the given device type has CPU load larger than 90%,
  send an email to a given address that "Device fleet is overloaded"
* when one particular device in the fleet has a CPU load larger than 10%,
  send the `setText` action to another device with the text "X% CPU utilization",
  where the X is the "cpu_load" reading of the original device
* when on "Any" device the free memory is below 104857600 (100MB), send the
  `blinkLed` action (sort of like warning lights)
* at midnight each day send the `setOff` signal to the entire fleet

... and a lot more possibilities.

A handy way to test actions, is triggering them manually, by using the corresponding
"test" button on the Rules dashboard.

## License

Copyright 2016 Rulemotion Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
