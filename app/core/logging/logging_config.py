import logging
import sys
from datetime import datetime
from pathlib import Path
from functools import lru_cache

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Custom formatter with timestamps


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return super().format(record)


@lru_cache()
def setup_logging():
    logger = logging.getLogger('auth_logger')
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = CustomFormatter(
        '%(timestamp)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = logging.FileHandler(logs_dir / 'auth.log')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = CustomFormatter(
        '%(timestamp)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
