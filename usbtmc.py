#!/usr/bin/python

import os
import re
import time

class UsbTMC(object):
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

    def close(self):
        os.close(self.FILE)

    def write(self, command):
        os.write(self.FILE, command)
        # The Rigol docs say to wait a bit after each command.
        time.sleep(0.1)

    def read(self, length=4000):
        return os.read(self.FILE, length)

    def ask(self, command, length=4000):
        self.write(command)
        return self.read(length)

    def ask_float(self, command):
        return float(self.ask(command))

    def ask_for_values(self, command):
        c = self.ask(command)
        float_regex = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\d*\.\d+)" "(?:[eE][-+]?\d+)?")
        vs = [float(raw_value) for raw_value in float_regex.findall(c)]
        return vs

    def get_name(self):
        return self.ask("*IDN?")

    def send_reset(self):
        self.write("*RST")
