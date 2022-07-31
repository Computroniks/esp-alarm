# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

"""
Unified logging This file provides unified and consistent logging
across the entire application in order to aid processing using external
tools. Based upon
https://github.com/louislam/uptime-kuma/blob/39aa0a7f07644ecdd99e0a8ddacbbb24e2afd931/src/util.ts#L61-L148
"""

import time
import sys


def log(module: str, msg: str, level: str) -> None:
    """
    log Create a log entry to stdout
    Create a standardised log entry to stdout with information on
    where it came from as well as the log level
    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    :param level: Log level
    :type level: str
    """

    level = level.upper()
    current_time = time.time_ns()
    formatted_message = "{} [{}] {}: {}".format(current_time, module, level, msg)

    print(formatted_message)

def dev(module: str, msg: str) -> None:
    """
    dev Write development log
    This should only be used for development as it is hidden
    normally in order to prevent overly verbose logs
    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    """

    log(module, msg, "dev")

def debug(module: str, msg: str) -> None:
    """
    debug Write debug log
    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    """

    log(module, msg, "debug")

def info(module: str, msg: str) -> None:
    """
    info Write info log
    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    """

    log(module, msg, "info")

def warn(module: str, msg: str) -> None:
    """
    warn Write warn log
    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    """

    log(module, msg, "warn")

def error(module: str, msg: str) -> None:
    """
    error Write error log
    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    """

    log(module, msg, "error")

def fatal(module: str, msg: str) -> None:
    """
    fatal Write fatal log

    Write a fatal log entry then soft reset using sys.exit(1)

    :param module: Section of application log originates from
    :type module: str
    :param msg: Log message
    :type msg: str
    """

    log(module, msg, "fatal")
    sys.exit(1)
