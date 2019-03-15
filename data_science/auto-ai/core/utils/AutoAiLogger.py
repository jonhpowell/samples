#!/usr/bin/env python3

import logging

# Title: Auto-AI Logger
#
# Description: for debugging and operational monitoring, output messages in a standard format. A necessity for
#   debugging event-based, async programs.
#
# Notes:
#
# TODO:
#


class AutoAiLogger(object):

    '''
        name: identifier (such as class name) to uniquely identify this logger instance
    '''
    def __init__(self, name, level=logging.DEBUG):
        self.location = name
        logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.DEBUG)
        self.log = logging.getLogger(name)
        self.log.debug(f"logger initialized, at level {level}")

    def debug(self, message):
        self.log.debug(message)

    def warning(self, message):
        self.log.warning(message)

    def info(self, message):
        self.log.info(message)

    def error(self, message):
        self.log.error(message)

    def fatal(self, message):
        self.log.fatal(message)


if __name__ == '__main__':      # simple test

    logger = AutoAiLogger('MyTestClass', logging.DEBUG)
    logger.fatal('Fatal level message')
    logger.error('Error level message')
    logger.info('Info level message')
    logger.debug('Debug level message')
