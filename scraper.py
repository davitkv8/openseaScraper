import os
import json

import tls_client

from base import logger
from namings import QUERY_DETAILS_MAP, AvailableQueries
from browser_session import BrowserSession


def get_nested_key(data, target_key):
    """
    Recursively searches for a key in a nested dictionary and returns its value.

    :param data: Dictionary to search in.
    :param target_key: Key to find in the dictionary.
    :return: The value of the target key if found, otherwise None.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Recursively search in the value if it's a dictionary or list
            nested_result = get_nested_key(value, target_key)
            if nested_result is not None:
                return nested_result
    elif isinstance(data, list):
        for item in data:
            nested_result = get_nested_key(item, target_key)
            if nested_result is not None:
                return nested_result

    return None


class OpenSeaScraper:
    """Open sea scraper."""

    # SHOULD THIS CLASS BE IMPLEMENTED AS A SINGLETON ???

    SAVED_REQUEST_FILE_PATH = "saved_request.json"

    def __init__(self, request_names: AvailableQueries):
        self.request_names = request_names
        self.session_maker = BrowserSession(self.request_names)

        # If we haven't request details stored yet
        if os.path.getsize(self.SAVED_REQUEST_FILE_PATH) == 0:
            self.session_maker.run()

        # Initializes a TLS client session
        self.session = tls_client.Session(
            client_identifier="chrome_112",  # Mimics Chrome v112
            random_tls_extension_order=True,  # Randomize TLS extension order
        )

        # Load the saved request details
        with open(self.SAVED_REQUEST_FILE_PATH, "r") as file:
            self.saved_request = json.load(file)


    def get_data(self):
        """get data."""

        # Make the request based on the saved method
        for request_name in self.request_names:
            request_body = QUERY_DETAILS_MAP[request_name]["body"]
            request_details = self.saved_request[request_name]
            proxy_map = request_details["proxy_map"]

            # Extract details from the saved request
            url = request_details["url"]
            method = request_details["method"]
            headers = request_details["headers"]
            cookies = {cookie["name"]: cookie["value"] for cookie in request_details["cookies"]}

            self.session.proxies = proxy_map

            if method == "POST":
                response = self.session.post(
                    url,
                    headers=headers,
                    # cookies=cookies,
                    json=request_body,
                )

            elif method == "GET":
                response = self.session.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                )

            else:
                logger.warning(f"Unsupported method '{method}'")
                exit()

            try:
                serialized_resp = response.json()
                data = get_nested_key(serialized_resp, "edges")
                logger.info(f"Data fetched - {data}")

            except json.JSONDecodeError as e:
                logger.warning(f"Could not decode JSON response from {url}, {e}")

