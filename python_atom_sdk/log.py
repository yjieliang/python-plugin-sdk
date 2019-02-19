# -*- coding: utf-8 -*-

import sys
import logging


LOG_NAME = "ATOM_LOG"
LOG_FORMAT = "[%(levelname)s]: %(message)s"
LOG_LEVEL = logging.DEBUG


def getLogger():
    logger = logging.getLogger(LOG_NAME)
    if logger.handlers:
        return logger
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(LOG_FORMAT)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    logger.addHandler(console)

    return logger
