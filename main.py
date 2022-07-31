# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

"""
Main entrypoint for ESP8266 based environment monitor
"""

import gc

import alarm

if __name__ == "__main__":
    gc.collect()

    alarm.main()
