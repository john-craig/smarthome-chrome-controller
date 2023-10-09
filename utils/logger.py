import logging
from logging.handlers import RotatingFileHandler
import datetime

class Logger():
    def __init__(self, log_path):
        logger = logging.getLogger("controller_logger")
        logger.setLevel(logging.INFO)

        # Create a rotating file handler to log to the specified file
        handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=3)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # Set the formatter for the handler
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

        self.logger = logger
    
    def log_event(self, message):
        self.logger.info(message)
