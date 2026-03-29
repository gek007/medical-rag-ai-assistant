import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

_fmt = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

"""
Logger Setup and Usage

This module provides a utility function `get_logger` to set up application-wide logging.

How it works:
- Logging output gets written both to the console (INFO and above) and to a rotating file log (DEBUG and above).
- Log entries include the timestamp, level, logger name, and message.
- Log files are stored under a `logs` directory at the project root.

How to set up:
- No extra setup is needed if this module is present in your project and importable.
- The logs directory will be created automatically if it doesn't exist.

How to use:
1. Import `get_logger` in any module where you need logging:
    from server.config.logger import get_logger

2. Get a logger for the module, typically using `__name__`:
    logger = get_logger(__name__)

3. Use standard logging methods:
    logger.info("This is an info message.")
    logger.error("This is an error message.")

All logs will appear in both the console and in `logs/app.log` (with rotation).

================================

# TERMINAL only — remove file handler
logger.addHandler(console_handler)
# logger.addHandler(file_handler)   ← comment out to disable file logging

# FILE only — remove console handler
# logger.addHandler(console_handler)  ← comment out to disable terminal logging
logger.addHandler(file_handler)

# BOTH (current default)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

====================================

2. Log file path
The path is built dynamically from config/logger.py lines 5–8:

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")
__file__ is config/logger.py, so dirname(dirname(...)) goes up two levels to the server/ folder:

server/
├── config/
│   └── logger.py      ← __file__
├── logs/              ← LOG_DIR (auto-created)
│   └── app.log        ← LOG_FILE  ✅
Absolute path on your machine:

G:/VSCode/medical-rag-ai-assistant/server/logs/app.log
When the file reaches 5 MB, it rotates automatically:

logs/app.log        ← current
logs/app.log.1      ← previous
logs/app.log.2      ← older
logs/app.log.3      ← oldest (max 3 backups)



"""


def get_logger(name: str) -> logging.Logger:
    """
    Returns a module-specific logger instance, configured for both console and file output.
    Ensures handlers are not duplicated for repeated calls with the same logger name.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(_fmt)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
