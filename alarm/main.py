# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

"""
Main entrypoint for 
"""

import sys

from .utils import alarm, initWLAN, readSettings
from .HTTP import HTTP
from .logging import debug, info, warn, error, fatal


def main() -> None:    
    settings = readSettings()
    if not initWLAN(settings["SSID"], settings["KEY"], settings["TIMEOUT"], settings["STATIC"], settings["ADDR"], settings["MASK"], settings["GATEWAY"]):
        print("ERROR Could not connect to Wi-Fi network")
        sys.exit(1)
    
    server = HTTP(settings["PORT"], settings["MAX_CON"], settings["ADDR_FAMILY"])
    server.listen()