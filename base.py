"""Module containing shared functionality and data around modules."""

import os
import logging
from typing import TypedDict

from dotenv import load_dotenv


__all__ = [
    "ProxyService",
    "logger",
]

# Load .env file
load_dotenv()

class ProxyMap(TypedDict):
    """Class representing a proxy map details (HTTP/S proxy addresses)."""

    http: str
    https: str


class ProxyService:
    """Proxy service class."""

    BASE_PROXY_URL = os.getenv("BASE_PROXY_URL")

    def generate_proxy(self, session_id) -> ProxyMap:
        """Generate a proxy string with a unique session ID."""

        username, password = self.BASE_PROXY_URL.split("@")[0].split("//")[1].split(":")
        proxy_host_port = self.BASE_PROXY_URL.split("@")[1]

        session_username = username.replace("session-X", f"session-{session_id}")

        http_proxy = f"http://{session_username}:{password}@{proxy_host_port}"
        https_proxy = f"https://{session_username}:{password}@{proxy_host_port}"

        return {
            "http": http_proxy,
            "https": https_proxy,
        }


def setup_logger():
    # Create a logger
    app_logger = logging.getLogger("app_logger")
    app_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    app_logger.addHandler(file_handler)
    app_logger.addHandler(console_handler)

    return app_logger


logger = setup_logger()
