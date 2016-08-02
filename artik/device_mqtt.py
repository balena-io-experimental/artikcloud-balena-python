import common
import certifi
import paho.mqtt.client as mqtt

ARTIK_MQTT_URL = "api.artik.cloud"
ARTIK_MQTT_PORT = 8883

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("/v1.1/actions/{}".format(common.DEVICE_ID))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_log(client, userdata, level, buf):
    print(buf)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log

print("Connecting!")
client.username_pw_set(common.DEVICE_ID, password=common.DEVICE_TOKEN)
client.tls_set(certifi.where())
client.connect_async(ARTIK_MQTT_URL, ARTIK_MQTT_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
