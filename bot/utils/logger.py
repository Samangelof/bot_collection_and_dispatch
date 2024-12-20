import logging
import sys
import os
from datetime import datetime


log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
current_date = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(log_directory, f"Bot_{current_date}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def log_info(message: str):
    """Функция для записи информационных сообщений в лог."""
    logging.info(message)

def log_error(message: str):
    """Функция для записи сообщений об ошибках в лог."""
    logging.error(message)

def log_warning(message: str):
    """Функция для записи предупреждений в лог."""
    logging.warning(message)
