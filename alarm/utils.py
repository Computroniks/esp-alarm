# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

"""
Utility methods for use with the alarm
"""

import network
import time
import sys
import os
import re
from machine import Pin

from .logging import debug, info, warn, error, fatal

def initWLAN(SSID: str, key: str, timeout: int = 10, static: bool = False, ip: str = None, mask: str = None, gateway: str = None) -> bool:
    """
    initWLAN Initialize wireless networking

    Initialize the onboard wireless networking interface to connect to
    the specified wireless network

    :param SSID: SSID to connect to
    :type SSID: str
    :param key: Key to use when connecting
    :type key: str
    :param timeout: How long should we wait before failing to connect?,
        defaults to 10
    :type timeout: int, optional
    :param static: Should a static IP be used?, defaults to False
    :type static: bool, optional
    :param ip: IP to use, defaults to None
    :type ip: str, optional
    :param mask: Subnet mask to use, defaults to None
    :type mask: str, optional
    :param gateway: Gateway to use, defaults to None
    :type gateway: str, optional
    :return: Was connection successfull?
    :rtype: bool
    """

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if static:
        # We don't use DNS so just set it to ourselves
        info("Network", "Settings static IP")
        sta_if.ifconfig((ip, mask, gateway, "127.0.0.1"))
    sta_if.connect(SSID, key)

    timeout = 10
    start = time.time()
    while not sta_if.isconnected():
            if (time.time() - start) > timeout:
                break

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    info("Network", "Config {}".format(sta_if.ifconfig()))
    return sta_if.isconnected()

def readSettings() -> dict:
    """
    readSettings Read the settings

    Reads settings from the settings file then parse them and return a
    dict of values.

    :return: Dict of values
    :rtype: dict
    """

    settings_model = {
        "SSID": {
            "type": str,
            "required": True,
            "required_if": None,
            "default": None,
            "regex": None
        },
        "KEY": {
            "type": str,
            "required": True,
            "required_if": None,
            "default": None,
            "regex": None
        },
        "MAX_CON": {
            "type": int,
            "required": False,
            "required_if": None,
            "default": 5,
            "regex": None
        },
        "TIMEOUT": {
            "type": int,
            "required": False,
            "required_if": None,
            "default": 10,
            "regex": None
        },
        "PORT": {
            "type": int,
            "required": False,
            "required_if": None,
            "default": 80,
            "regex": None
        },
        "STATIC": {
            "type": bool,
            "required": False,
            "required_if": None,
            "default": False,
            "regex": "^(TRUE|FALSE)$"
        },
        "ADDR": {
            "type": str,
            "required": False,
            "required_if": "STATIC",
            "default": None,
            "regex": None # Can't validate IP here as MicroPython doesn't yet support full regex
        },
        "MASK": {
            "type": str,
            "required": False,
            "required_if": "STATIC",
            "default": None,
            "regex": None
        },
        "GATEWAY": {
            "type": str,
            "required": False,
            "required_if": "STATIC",
            "default": None,
            "regex": None 
        },
        "ADDR_FAMILY": {
            "type": str,
            "required": False,
            "required_if": "STATIC",
            "default": None,
            "regex": "^(INET|INET6)$"
        }
    }

    if "settings.txt" not in os.listdir():
        print("ERROR No settings.txt file found")
        sys.exit(1)
    
    settings = {}
    
    with open("settings.txt", "r") as f:
        for i in f.readlines():
            line = i.replace("\n", "").replace("\r", "").split("=")

            # Make sure we only use valid setting keys
            if line[0] in settings_model:
                settings[line[0]] = line[1]
            else:
                continue
    
    # Validate settings
    for i in settings_model:
        debug("Settings", "Validating {}".format(i))
        if i in settings:
            debug("Settings", "Found {} in settings file".format(i))
            if settings_model[i]["regex"] is not None and settings_model[i]["type"] == str:
                pattern = re.compile(settings_model[i]["regex"])
                if not pattern.match(settings[i]):
                    fatal("Settings", "Value of {} does not match regex".format(i))

            debug("Settings", "Expected type is {}".format(settings_model[i]["type"]))
            if settings_model[i]["type"] == bool:
                settings[i] = settings[i].upper() == "TRUE"
            else:
                try:
                    settings[i] = settings_model[i]["type"](settings[i])
                except ValueError:
                    fatal("Settings", "{} is of wrong type. Found {}. Expected {}.".format(i, type(settings[i]), settings_model[i]["type"]))
        else:
            if settings_model[i]["required"]:
                fatal("Settings", "Required setting {} not present in settings file".format(i))
            if settings_model[i]["required_if"]:
                if settings[settings_model[i]["required_if"]]:
                    fatal("Settings", "Setting {} required as setting {} is set to True".format(i, settings_model[i]["required_if"]))
            
            info("Settings", "{} not found in settings. Using default of {}".format(i, settings_model[i]["default"]))
            settings[i] = settings_model[i]["default"]
        
    return settings

def getSubstringFromList(strings: list, substring: str) -> int:
    """
    getSubstringFromList Get index of first instance of string

    :param strings: List to search
    :type strings: list
    :param substring: Substring to search for
    :type substring: str
    :return: Index. -1 if not found
    :rtype: int
    """

    for i, s in enumerate(strings):
        if substring in s:
              return i
    return -1

def alarm(buzzer: Pin, enabled_for: int, on: int, off: int) -> None:
    """
    alarm Activate the buzzer

    Activate the buzzer for the specified length of time turning it on
    and off for the specified miliseconds.

    :param buzzer: Buzzer to activate
    :type buzzer: machine.Pin
    :param enabled_for: Time to activate buzzer for
    :type enabled_for: int
    :param on: Time buzzer should spend on
    :type on: int
    :param off: Time buzzer should spend off
    :type off: int
    """

    start = time.ticks_ms()


    while time.ticks_diff(time.ticks_ms(), start) < enabled_for:
        buzzer.on()
        time.sleep_ms(on)
        buzzer.off()
        time.sleep_ms(off)
