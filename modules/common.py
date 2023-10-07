"""
Commonly used functions and objects.
"""
import time

def ms_time(value=False):
    """
    Return current time (or provided timestamp) as integers in milliseconds .
    """
    if not value:
        value = time.time()
    return int(value * 1000)

def ms_sleep(value):
    """
    Sleep given time in milliseconds
    """
    time.sleep(value / 1000)

def build_url(address, port, slug=False):
    """
    Build url from address, port and optional slug.
    """
    if slug:
        return "http://{}:{}/{}".format(address, port, slug)
    else:
        return "http://{}:{}/".format(address, port)

def get_granularity(granularity):
    """Convert frequencies to milliseconds.
    """
    freqs = {
        "H": 60 * 60,
        "M": 60,
        "S": 1,
        "D": 24 * 60 * 60,
    }
    number, letter = int(granularity[:-1]), granularity[-1].upper()
    return ms_time(number * freqs[letter])
