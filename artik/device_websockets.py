"""
WebSockets Client for ARTIk Cloud

For additional details, see:
* https://developer.artik.cloud/documentation/connect-the-data/rest-and-websockets.html
* https://developer.artik.cloud/documentation/api-reference/websockets-api.html
"""
import json
import time
import threading

from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS

import common

# Settings
ARTIKCLOUD_WEBSOCKETS_URL = "wss://api.artik.cloud/v1.1/websocket?ack=true"
ARTIKCLOUD_WEBSOCKETS_DOMAIN = "api.artik.cloud"
ARTIKCLOUD_WEBSOCKETS_PORT = 443
ARTIKCLOUD_AUTH_HEADER = {"Authorization": "bearer {}".format(common.DEVICE_TOKEN)}

worker_stop = threading.Event()

class ArtikClientProtocol(WebSocketClientProtocol):

    """
    ARTIK Cloud WebSockets client that generates stream of data readings and
    acts upon the received actions
    """

    def onConnect(self, response):
        """Callback for when the server is connected
        """
        print("Server connected: {}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        """Callback for when connection opened to the server
        """
        print("Connected")
        # Register to receive messages
        register_message = {
            "sdid": "{}".format(common.DEVICE_ID),
            "Authorization": "bearer {}".format(common.DEVICE_TOKEN),
            "type": "register",
            }
        self.sendMessage(json.dumps(register_message))
        worker_stop.clear()
        t = threading.Thread(target=worker, args=(self, worker_stop))
        t.daemon = True
        t.start()

    def onClose(self, wasClean, code, reason):
        """Callback when the WebSockets connections closed
        """
        print("WebSocket connection closed: {}".format(reason))
        worker_stop.set()

    def onMessage(self, payload, isBinary):
        """Callback for when a message is received from the server
        """
        print(payload)
        try:
            data = json.loads(payload)
        except json.decoder.JSONDecodeError:
            print("Can't decode payload: {}".format(payload))
        else:
            if "type" in data.keys() and data['type'] == 'action':
                handle_actions(data['data']['actions'])


class ArtikClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    protocol = ArtikClientProtocol

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)


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

def worker(client, stop):
    """ Worker thread: periodic sensor readings and publishing to ARTIK Cloud
    """
    i = 0
    while not stop.is_set():
        if i % common.READINGS_PERIOD == 0:
            message = {
                "sdid":"{}".format(common.DEVICE_ID),
                "type": "message",
                "data": {
                    "cpu_load": common.reading_cpu(),
                    "free_memory": common.reading_memory(),
                    "random": common.reading_random()
                },
                "ts": int(round(time.time() * 1000)),
            }
            print(message)
            client.sendMessage(json.dumps(message))
            i = 1
        else:
            i += 1
        time.sleep(1)

if __name__ == '__main__':

    ## Not reconnecting WebSockets
    # factory = WebSocketClientFactory(ARTIKCLOUD_WEBSOCKETS_URL, headers=ARTIKCLOUD_AUTH_HEADER)
    # factory.protocol = ArtikClientProtocol
    # connectWS(factory)
    # reactor.run()

    ## Reconnecting WebSockets
    factory = ArtikClientFactory(ARTIKCLOUD_WEBSOCKETS_URL, headers=ARTIKCLOUD_AUTH_HEADER)
    factory.protocol = ArtikClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(ARTIKCLOUD_WEBSOCKETS_DOMAIN, ARTIKCLOUD_WEBSOCKETS_PORT,
                       factory, contextFactory, common.TIMEOUT)
    reactor.run()
