import sys
import os
from Adafruit_IO import MQTTClient


# Adafruit credentials
ADAFRUIT_IO_KEY = os.environ.get("IO_KEY")
ADAFRUIT_IO_USERNAME = os.environ.get("IO_USERNAME")
ADAFRUIT_FEED_ID = 'crypto-covid'


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(ADAFRUIT_FEED_ID))


def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(ADAFRUIT_FEED_ID, granted_qos[0]))


def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)


def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))


def publish(client, userdata, topic, pid):
    # This method is called when the client publishes data to a feed.
    print('Published to {0} with PID {1}'.format(topic, pid))


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print('Unsubscribed from {0} with PID {1}'.format(topic, pid))


def send_ada(data):
    # Create an MQTT client instance.
    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Setup the callback functions defined above.
    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.on_subscribe = subscribe
    client.on_unsubscribe = unsubscribe
    client.on_publish = publish

    # Connect to the Adafruit IO server.
    client.connect()
    client.subscribe(ADAFRUIT_FEED_ID)
    client.publish(ADAFRUIT_FEED_ID, data)
    client.unsubscribe(ADAFRUIT_FEED_ID)
    client.disconnect()