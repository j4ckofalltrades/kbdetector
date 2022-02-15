#!/usr/bin/env python

import argparse
import re
import subprocess
from sys import platform


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-dongle", action="store_true", help="exclude keyboard dongles and/or receivers")
    return parser.parse_args()


def lsusb_detect():
    result = []

    device_pattern = b"Bus\\s+(?P<bus>\\d+)\\s+Device\\s+(?P<device>\\d+).+ID\\s(?P<id>\\w+:\\w+)\\s(?P<tag>.+)$"
    device_re = re.compile(device_pattern, re.I)
    devices = subprocess.check_output("lsusb -v 2>/dev/null | egrep '(^Bus|Keyboard)' | grep -B1 Keyboard", shell=True)

    for device in devices.split(b'\n'):
        if device:
            info = device_re.match(device)
            if info:
                device_info = info.groupdict()
                keeb_info = str(device_info['tag']).replace('b\'', '').replace('\'', '')
                result.append(keeb_info)

    return result


def filter_keebs(kbs: list):
    filtered = filter(lambda k: "Receiver" not in str(k) and "Dongle" not in str(k), kbs)
    return list(filtered)


def print_keebs(kbs: list):
    if len(kbs) > 0:
        for kb in kbs:
            k = u'\U00002328'
            print(f'{k}  {kb}')
    else:
        print("No keyboards detected...")


if __name__ == '__main__':
    print("""
     _             _         
    | | _____  ___| |__  ___ 
    | |/ / _ \/ _ \ '_ \/ __|
    |   <  __/  __/ |_) \__ \ 
    |_|\_\___|\___|_.__/|___/
    """)

    args = parse_args()

    if "linux" in platform:
        keebs = filter_keebs(lsusb_detect()) if args.no_dongle else lsusb_detect()
        print_keebs(keebs)
    elif "darwin" in platform:
        print("TODO: add MacOS support")
    elif "windows" in platform:
        print("TODO: add Windows support")
    else:
        print("Unsupported platform: " + platform)
