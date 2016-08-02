"""
MQTT Client for ARTIk Cloud
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

cond = threading.Condition()
worker_stop = None

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # If connected cleanly
    if rc == 0:
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("/v1.1/actions/{}".format(common.DEVICE_ID))
        global worker_stop
        worker_stop = threading.Event()
        t = threading.Thread(target=worker, args=(client, worker_stop))
        t.daemon = True
        t.start()

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code "+str(rc))
    global worker_stop
    worker_stop.set()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    try:
        data = json.loads(msg.payload)
    except Exception as e:
        raise
    if "actions" in data:
        handle_actions(data['actions'])

def on_log(client, userdata, level, buf):
    print(buf)

def worker(client, stop):
    """ Worker thread
    """
    i = 0
    while (not stop.is_set()):
        if i % common.READINGS_PERIOD == 0:
            readings = {
                "cpu_load": common.reading_cpu(),
                "free_memory": common.reading_memory(),
                "random": common.reading_random()
            }
            print(readings)
            client.publish(PUBLISH_CHANNEL, json.dumps(readings))
            i = 1
        else:
            i += 1
        time.sleep(1)

def handle_actions(actions):
    for action in actions:
        if action['name'] == 'setText':
            common.setText(action['parameters']['text'])
        elif action['name'] == 'blinkLed':
            common.blinkLed()
        elif action['name'] == 'setOff':
            common.setOff()
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
    # client.loop_start()
    # client.connect(ARTIK_MQTT_URL, ARTIK_MQTT_PORT, 60)
    client.connect(ARTIK_MQTT_URL, ARTIK_MQTT_PORT, keepalive=15)
    # client.loop_start()
    client.loop_forever()
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.

    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Exiting!")

    # while True:
    #     print(CONNECTED)
    #     readings = {
    #         "cpu_load": common.reading_cpu(),
    #         "free_memory": common.reading_memory(),
    #         "random": common.reading_random()
    #         }
    #     print(readings)
    #     client.publish(PUBLISH_CHANNEL, json.dumps(readings))
    #     time.sleep(common.READINGS_PERIOD)
