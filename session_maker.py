"""This module generates and stores all essential request details via playwright if TLS Client fails during the handshake."""

import time
import json
import sys
import os

from playwright.sync_api import sync_playwright

from base import logger
from namings import QUERY_DETAILS_MAP


class SessionMaker:
    """Session maker class."""

    GRAPHQL_BACKEND_API_URL = "https://opensea.io/__api/graphql/"

    def __init__(self, request_names: list[str], timeout: int = 5000):
        self.request_names = request_names
        self.timeout = timeout


    def handle_route(self, route, request, context, request_key):
        """Function to intercept, track and modify targeted request."""

        if request.url == self.GRAPHQL_BACKEND_API_URL and request.method == "POST":
            query_name = QUERY_DETAILS_MAP[request_key]["query_name"]  # RankingsPageTopQuery, RankingsPageTrendingQuery .....
            post_data = request.post_data
            if post_data and query_name in post_data:
                # Request details dict.
                saved_request = {
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers,
                    "cookies": context.cookies(),  # Save cookies from the browser context
                    "post_data": json.loads(post_data),
                }

                self._save_request_details(request_key, saved_request)

                # Modify the payload (if needed)
                # modified_payload = json.loads(post_data)
                # modified_payload["variables"]["timeWindow"] = "ALL_TIME"
                # modified_payload["variables"]["count"] = 100
                return
            else:
                route.continue_()
        else:
            route.continue_()

    def run(self):
        """Runner function."""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            print(self.request_names)

            # Register handlers simultaneously
            for request_name in self.request_names:
                page_url = QUERY_DETAILS_MAP[request_name]["accessor_page_url"]
                page.route("**/__api/graphql/**", lambda route, request: self.handle_route(route, request, context, request_name))
                page.goto(page_url)
                time.sleep(1)

            page.wait_for_timeout(self.timeout)  # Wait for network activity for 10 seconds

            logger.info("Timeout reached, closing browser...")
            browser.close()

    def _save_request_details(self, request_key, request_details):
        """Function saves request details into json file."""
        try:
            # Read the existing JSON data
            with open("saved_request.json", 'r') as file:
                data = json.load(file) if os.path.getsize("saved_request.json") else {}

            data[request_key] = request_details

            # Write the updated data back to the file
            with open("saved_request.json", 'w') as file:
                json.dump(data, file, indent=4)

            logger.info(f"Request details saved: {request_key} - {request_details}")
        except Exception as e:
            logger.warning(f"An error occurred: {e}")
