# -*- coding: utf-8 -*-

import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def install():
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
