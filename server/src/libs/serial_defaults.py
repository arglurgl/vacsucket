#!/usr/bin/env python

import serial
from .config import CONFIG


# CONFIG = {
#    "serial": {
#        'baudrate': 9600,
#        'port': '/dev/ttyUSB0',
#        #'timeout': 1,
#        #'bytesize': serial.EIGHTBITS,
#        #'parity': serial.PARITY_NONE,
#        #'stopbits': serial.STOPBITS_ONE,
#    }
# }


def Serial(*args, **kwargs):
    """
    Create Serial connection with PROFILE defaults.
    Args and kwargs always override PROFILE settings.
    """
    config = CONFIG["serial"]
    config.update(kwargs)

    # If port is provided as first positional argument
    if args:
        config["port"] = args[0]

    return serial.Serial(**config)


con = Serial()
