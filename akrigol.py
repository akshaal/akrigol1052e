#!/usr/bin/python
# Copyright (c) 2017, Akshaal blahblahblah, GNU GPL blahblahblah

import os
import re
import time
import subprocess
import scope
import shelve

DEVICE_PATH = '/dev/usbtmc2'
PADL = 40 # well, padding width or something like this

def make_scope_instance():
    return scope.DS1000(DEVICE_PATH, 2)

def make_timestamp(obj):
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
    print(name.ljust(PADL) + "  : " + scope.ask(cmd))

def ask_and_print_float(name, cmd, suff = "", f = identity):
    v = f(scope.ask_float(cmd))
    print(name.ljust(PADL) + "  : " + str(v) + suff)

def ask_and_print_float0(name, cmd, suff = "", f = identity):
    v = f(scope.ask_for_values(cmd)[0])
    print(name.ljust(PADL) + "  : " + str(v) + suff)

def print_sep():
    print("=======================================================================")

