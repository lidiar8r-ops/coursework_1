# app_logger.py
import logging
import os
from logging import Logger

from src.config import LOG_DIR

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

def get_file_handler(name):
    file_handler = logging.FileHandler(os.path.join(LOG_DIR,name), "w", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name: object) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler(name))
    logger.addHandler(get_stream_handler())
    return logger
