#!/usr/bin/python

import os
import re
import time

l = 40

def with_units(d, m, u, n, K, M, G):
    def f(x):
        z = abs(x)
        if z < (0.1 / 1000.0 / 1000.0):
            return str(x * 1000000000.0) + n
        elif z < (0.1 / 1000.0):
            return str(x * 1000000.0) + u
        elif z < 0.1:
            return str(x * 1000.0) + m
        elif z > 10000000000:
            return str(x / 1000000000.0) + G
        elif z > 10000000:
            return str(x / 1000000.0) + M
        elif z > 10000:
            return str(x / 1000.0) + K
        else:
            return str(x) + d
    return f

as_time = with_units(" s", " ms", " us", " ns", " Kilo-seconds", "Mega-seconds", " Giga-seconds")
as_volt = with_units(" V", " mV", " uV", " nV", " KV", "MV", " GV")
as_hz = with_units(" hz", " mhz", " uhz", " nhz", " Khz", "Mhz", " Ghz")
as_wtf = with_units(" h", " m", " u", " n", " K", "M", " G")

def identity(x):
    return x

def ask_and_print(name, cmd):
    print(name.ljust(l) + "  : " + scope.ask(cmd))

def ask_and_print_float(name, cmd, suff = "", f = identity):
    v = f(scope.ask_float(cmd))
    print(name.ljust(l) + "  : " + str(v) + suff)

def ask_and_print_float0(name, cmd, suff = "", f = identity):
    v = f(scope.ask_for_values(cmd)[0])
    print(name.ljust(l) + "  : " + str(v) + suff)

def print_sep():
    print("=======================================================================")


class UsbTMC(object):
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device = "/dev/usbtmc2"):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

    def close(self):
        self.write(":KEY:LOCK DISABLE")
        os.close(self.FILE)

    def write(self, command):
        os.write(self.FILE, command)
        # The Rigol docs say to wait a bit after each command.
        time.sleep(0.2)

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

scope = UsbTMC()
