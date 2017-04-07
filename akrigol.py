#!/usr/bin/python
# Copyright (c) 2017, Akshaal blahblahblah, GNU GPL blahblahblah

import os
import sys
import re
import time
import subprocess
import scope
import shelve
import datetime
import numpy as np
from math import sqrt

DEVICE_PATH = '/dev/usbtmc2'
PADL = 40 # well, padding width or something like this

def log_stdout():
    # Unbuffer output
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    tee = subprocess.Popen(["tee", "-a", "out/log.txt"], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

log_stdout()

def make_scope_instance():
    return scope.DS1000(DEVICE_PATH, 2)

def make_timestamp(obj = None):
    if not obj:
        obj = datetime.datetime.now()
    return obj.strftime("%Y-%m-%d %H.%M.%S")

def serialize(name, data, dobj):
    def write(suffix):
        fname = "out/" + name + suffix + ".db"
        print("Writing: " + fname)
        db = shelve.open(fname)
        db['data'] = data
        db.close()

    write("")
    write("-" + make_timestamp(dobj))

def deserialize(name):
    fname = "out/" + name + ".db"
    print("Reading: " + fname)
    db = shelve.open(fname)
    data = db['data']
    db.close()
    return data

def call(cmd_args, **kw):
    return subprocess.call (cmd_args, **kw)

# Dumb way to work with units....
def with_units(d, m, u, n, K, M, G):
    def f(x):
        try:
            z = abs(x)
            if z < (0.1 / 1000.0 / 1000.0):
                nx = x * 1000000000.0
                c = n
            elif z < (0.1 / 1000.0):
                nx = x * 1000000.0
                c = u
            elif z < 0.1:
                nx = x * 1000.0
                c = m
            elif z > 10000000000:
                nx = x / 1000000000.0
                c = G
            elif z > 10000000:
                nx = x / 1000000.0
                c = M
            elif z > 10000:
                nx = x / 1000.0
                c = K
            else:
                nx = x
                c = d

            nx = str(round(nx * 100.0) / 100.0)
            if "." in nx:
                nx = nx.rstrip("0")
                if nx.endswith("."):
                    nx = nx[:-1]

            return nx + c
        except:
            return str(x)
    return f

as_time = with_units(" s", " ms", " us", " ns", " Kilo-seconds", "Mega-seconds", " Giga-seconds")
as_volt = with_units(" V", " mV", " uV", " nV", " KV", "MV", " GV")
as_hz = with_units(" hz", " mhz", " uhz", " nhz", " Khz", "Mhz", " Ghz")
as_wtf = with_units("", " m", " u", " n", " K", "M", " G")

def identity(x):
    return x

def print_sep():
    print("=======================================================================")

class UsbTMC(object):
    def __init__(self, device = DEVICE_PATH):
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

    def ask_and_print(self, name, cmd):
        print(name.ljust(PADL) + "  : " + self.ask(cmd))

    def ask_and_print_float(self, name, cmd, suff = "", f = identity):
        v = f(self.ask_float(cmd))
        print(name.ljust(PADL) + "  : " + str(v) + suff)

    def ask_and_print_float0(self, name, cmd, suff = "", f = identity):
        v = f(self.ask_for_values(cmd)[0])
        print(name.ljust(PADL) + "  : " + str(v) + suff)

    def do_and_close(self, f):
        try:
            f()
        finally:
            self.close()
