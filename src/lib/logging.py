import logging


class Logger(object):

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def from_module(module_name):
        return Logger(logging.getLogger(module_name))

    def info(self, msg, *args):
        self.logger.info(msg, *args)

    def warn(self, msg, *args):
        self.logger.warn(msg, *args)

    def error(self, msg, *args):
        self.logger.error(msg, *args)

    def critical(self, msg, *args):
        self.logger.critical(msg, *args)

    def exception(self, msg, *args):
        self.logger.exception(msg, *args)

    def debug(self, msg, *args):
        self.logger.debug(msg, *args)
