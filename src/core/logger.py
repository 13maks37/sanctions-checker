import logging
import logging.config
import os
import glob
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

LOG_DIR_GENERAL = "logs/general"
LOG_DIR_ERRORS = "logs/errors"

os.makedirs(LOG_DIR_GENERAL, exist_ok=True)
os.makedirs(LOG_DIR_ERRORS, exist_ok=True)


class ErrorLogFilter(logging.Filter):
    """Filter to level error and critical"""

    def filter(self, record):
        return record.levelno >= logging.ERROR


def clean_old_logs(log_dir, days=30):
    """Function for automatic log cleaning"""
    now = datetime.now()
    for file_path in glob.glob(os.path.join(log_dir, "*.log*")):
        try:
            mtime = os.path.getmtime(file_path)
            file_time = datetime.fromtimestamp(mtime)
            if now - file_time > timedelta(days=days):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete file {file_path}: {e}")


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """Handler for moving logs"""

    def __init__(self, log_dir, filename, **kwargs):
        os.makedirs(log_dir, exist_ok=True)
        full_path = os.path.join(log_dir, filename)
        super().__init__(
            filename=full_path,
            when="midnight",
            interval=1,
            backupCount=0,
            encoding="utf-8",
            **kwargs,
        )
        self.log_dir = log_dir
        self.suffix = "%Y-%m-%d"

    def doRollover(self):
        super().doRollover()
        clean_old_logs(self.log_dir, days=30)


# Config logger
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": (
                "%(filename)s:%(lineno)d #%(levelname)-8s "
                "[%(asctime)s] - %(name)s - %(message)s"
            )
        },
    },
    "filters": {
        "error_filter": {
            "()": ErrorLogFilter,
        }
    },
    "handlers": {
        "file": {
            "()": DailyRotatingFileHandler,
            "log_dir": LOG_DIR_GENERAL,
            "filename": "app.log",
            "level": "INFO",
            "formatter": "default",
        },
        "error_file": {
            "()": DailyRotatingFileHandler,
            "log_dir": LOG_DIR_ERRORS,
            "filename": "error.log",
            "level": "ERROR",
            "formatter": "default",
            "filters": ["error_filter"],
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        },
    },
    "root": {"level": "INFO", "handlers": ["file", "error_file", "console"]},
}
