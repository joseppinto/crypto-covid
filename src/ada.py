import os
from Adafruit_IO import Client


# Adafruit credentials
ADAFRUIT_IO_KEY = os.environ.get("IO_KEY")
ADAFRUIT_IO_USERNAME = os.environ.get("IO_USERNAME")
ADAFRUIT_FEED_ID = 'crypto-covid'

def send_ada(data):
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    aio.send(ADAFRUIT_FEED_ID, data)
