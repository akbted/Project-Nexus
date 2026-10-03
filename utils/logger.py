import logging
from logging import basicConfig, INFO

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Logger initialized.")

class Logger:
    def __init__(self, name):
        self.name = name

    def log(self, message):
        logger.info(f"{self.name}: {message}")