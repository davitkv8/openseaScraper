"""Module containing shared functionality and data around modules."""
import os
import logging
from dotenv import load_dotenv


__all__ = [
    "logger",
    "proxy_map",
]

# Load .env file
load_dotenv()


def setup_logger():
    # Create a logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

# Read the proxy value
proxy_http = os.getenv("proxy_http")
proxy_https = os.getenv("proxy_https")

proxy_map = {
    "http": proxy_http,
    "https": proxy_https,
}
