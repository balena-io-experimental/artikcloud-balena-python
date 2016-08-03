"""
Common functions for the ARTIK Cloud device, implementing sensor readings,
and device actions as defined by the applicable manifest.
"""
import os
import random

import psutil
import requests

###
# Settings
###
DEVICE_ID = os.getenv('ARTIKCLOUD_DEVICE_ID')
DEVICE_TOKEN = os.getenv('ARTIKCLOUD_DEVICE_TOKEN')
TIMEOUT = 60
try:
    READINGS_PERIOD = int(os.getenv('READINGS_PERIOD', 600))
except ValueError:
    # By default, do a reading every 600s = 10min, not to exhaust
    # the max message quota of the ARTIK Cloud free tier (150msg/day)
    READINGS_PERIOD = 600

###
# Get readings (output)
###
def reading_cpu(interval=0):
    """Reading CPU utilization

    Arguments:
    interval -- monitoring interval in seconds, default=0 (immediate)
    """
    return psutil.cpu_percent(interval=interval)

def reading_memory():
    """Reading amount of free memory (in bytes)
    """
    return psutil.virtual_memory().free

def reading_random(lower=0, upper=1):
    """Reading a random number from within an interval

    Arguments:
    lower -- lower bound of the interval, default=0
    upper -- upper bound of the interval, default=1
    """
    if lower > upper:
        lower, upper = upper, lower
    return random.uniform(lower, upper)

###
# Handle actions (input)
###
def action_set_off():
    """Turn device off through the Supervisor API
    """
    url = "{}/v1/shutdown?apikey={}".format(os.getenv('RESIN_SUPERVISOR_ADDRESS'),
                                            os.getenv('RESIN_SUPERVISOR_API_KEY'))
    requests.post(url)

def action_set_text(text=""):
    """Print text to the log

    Arguments:
    text -- the string to display, default=""
    """
    # This could be replaced with any other kind of text display
    print("setText: {}".format(text))

def action_blink_led():
    """Blink the device identification LED (when possible) through the
    Supervisor API
    """
    url = "{}/v1/blink?apikey={}".format(os.getenv('RESIN_SUPERVISOR_ADDRESS'),
                                         os.getenv('RESIN_SUPERVISOR_API_KEY'))
    requests.post(url)
