from logging import DEBUG
from logging import INFO
from logging import StreamHandler
from logging import Formatter

from .lib.logging import Logger


# Configure this manually if you are a developer
# TODO: ensure via build system that this is always set to INFO/WARNING for production.
log_level = INFO


# Logging setup ///////////////////////////////////////////////////////////////
# Define a top level logger for this package so all submodules inherit properties and settings.
top_level_logger = Logger.from_module(__name__.rsplit('.')[0])
top_level_logger.logger.setLevel(log_level)

_console_handler = StreamHandler()

_formatter = Formatter('[%(asctime)s|%(name)s|%(levelname)s] %(message)s')
_console_handler.setFormatter(_formatter)

top_level_logger.logger.addHandler(_console_handler)
# /////////////////////////////////////////////////////////////////////////////

from .commands import *
