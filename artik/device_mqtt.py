"""
MQTT Client for ARTIk Cloud

For additional details, see:
* https://developer.artik.cloud/documentation/connect-the-data/mqtt.html
* https://developer.artik.cloud/documentation/api-reference/mqtt-api.html
"""
import json
import time
import threading

import common
import certifi
import paho.mqtt.client as mqtt

# Settings
ARTIK_MQTT_URL = "api.artik.cloud"
ARTIK_MQTT_PORT = 8883
PUBLISH_CHANNEL = "/v1.1/messages/{}".format(common.DEVICE_ID)
ACTIONS_CHANNEL = "/v1.1/actions/{}".format(common.DEVICE_ID)

worker_stop = threading.Event()

def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server
    """
    print("Connected with result code "+str(rc))

    # If connected cleanly
    if rc == 0:
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(ACTIONS_CHANNEL)
        # Start readings
        worker_stop.clear()
        t = threading.Thread(target=worker, args=(client, worker_stop))
        t.daemon = True
        t.start()

def on_disconnect(client, userdata, rc):
    """Callback for when the client receives disconnects from the server.
    """
    print("Disconnected with result code "+str(rc))
    # Stop worker thread
    worker_stop.set()

def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server
    """
    print(msg.topic+" "+str(msg.payload))
    try:
        data = json.loads(msg.payload)
    except json.decoder.JSONDecodeError:
        print("Can't decode payload: {}".format(msg.payload))
    else:
        if "actions" in data:
            handle_actions(data['actions'])

def on_log(client, userdata, level, buf):
    """Callback on logging event, printing to the device log stream
    """
    print(buf)

def worker(client, stop):
    """ Worker thread: periodic sensor readings and publishing to ARTIK Cloud
    """
    i = 0
    while not stop.is_set():
        if i % common.READINGS_PERIOD == 0:
            # MQTT messages only contain the data, unlike other ARTIK Cloud clientConnectionLost
            # https://developer.artik.cloud/documentation/connect-the-data/mqtt.html#publish-data-only-messages
            data = {
                "cpu_load": common.reading_cpu(),
                "free_memory": common.reading_memory(),
                "random": common.reading_random()
            }
            print(data)
            client.publish(PUBLISH_CHANNEL, json.dumps(data))
            i = 1
        else:
            i += 1
        time.sleep(1)

def handle_actions(actions):
    """Handling incoming actions
    """
    for action in actions:
        if action['name'] == 'setText':
            common.action_set_text(action['parameters']['text'])
        elif action['name'] == 'blinkLed':
            common.action_blink_led()
        elif action['name'] == 'setOff':
            common.action_set_off()
        else:
            print("Unknown action: {}".format(action['name']))


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log

    print("Connecting!")
    client.username_pw_set(common.DEVICE_ID, password=common.DEVICE_TOKEN)
    client.tls_set(certifi.where())
    client.connect(ARTIK_MQTT_URL, ARTIK_MQTT_PORT, keepalive=common.TIMEOUT)
    client.loop_forever()
