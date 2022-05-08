#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight script to detect and print out all keyboards connected (via USB including dongles / wireless receivers) to
the machine, without any external dependencies.

Supports Linux and MacOS using the following built-in tools:

Linux - lsusb
MacOS - system_profiler
"""

import argparse
import re
import logging
import subprocess
from sys import platform

logging.basicConfig(level=logging.INFO, format='%(message)s')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exclude", help="comma-separated list of keyboards to exclude")
    parser.add_argument("-n", "--no-dongle", action="store_true", help="exclude keyboard dongles and/or receivers")
    return parser.parse_args()


def linux_detect_kbs():
    device_pattern = b"Bus\\s+(?P<bus>\\d+)\\s+Device\\s+(?P<device>\\d+).+ID\\s(?P<id>\\w+:\\w+)\\s(?P<tag>.+)$"
    device_re = re.compile(device_pattern, re.I)
    devices = subprocess.check_output(
        "lsusb -v 2>/dev/null | egrep '(^Bus|Keyboard)' | grep -B1 Keyboard",
        shell=True
    )

    result = []
    for device in devices.split(b'\n'):
        if device:
            match = device_re.match(device)
            if match:
                device_info = match.groupdict()
                keeb = str(device_info['tag']).replace('b\'', '').replace('\'', '')
                result.append(keeb)

    return result


def mac_detect_kbs():
    # collect all connected device names as no further information about device type is available
    devices = subprocess.check_output(
        """
        system_profiler SPUSBDataType | egrep -B 2 -A 6 'Product ID' | sed 's/^--/#/'\
            | egrep ':$' | sed -e 's/^ *//g' -e 's/ *:$//g'
        """,
        shell=True
    )

    result = []
    for device in devices.split(b'\n'):
        if device:
            keeb = str(device).replace('b\'', '').replace('\'', '')
            result.append(keeb)

    # filter out obvious false positives
    filtered = filter(
        lambda k: "hub" not in str(k).lower() and "mouse" not in str(k).lower() and "usb" not in str(k).lower(),
        result
    )

    return list(filtered)


def filter_dongles(kbs: list):
    filtered = filter(
        lambda k: "receiver" not in str(k).lower() and "dongle" not in str(k).lower(),
        kbs
    )
    return list(filtered)


def print_keebs(kbs: list):
    if kbs:
        for kb in kbs:
            k = u'\U00002328'
            logging.info('%s  %s', k, kb)
    else:
        logging.info("No keyboards detected...")


if __name__ == '__main__':

    logging.info("""
     _             _         
    | | _____  ___| |__  ___ 
    | |/ / _ \/ _ \ '_ \/ __|
    |   <  __/  __/ |_) \__ \ 
    |_|\_\___|\___|_.__/|___/
    """)

    args = parse_args()

    keebs = []
    if "linux" in platform:
        keebs = filter_dongles(linux_detect_kbs()) if args.no_dongle else linux_detect_kbs()
    elif "darwin" in platform:
        keebs = filter_dongles(mac_detect_kbs()) if args.no_dongle else mac_detect_kbs()
    else:
        logging.error("Unsupported platform: " + platform)
        exit(1)

    if args.exclude:
        exclude = args.exclude.split(",")
        filtered = [kb for kb in keebs if kb not in exclude]
        print_keebs(filtered)
    else:
        print_keebs(keebs)
