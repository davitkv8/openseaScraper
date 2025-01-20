"""This module generates and stores all essential request details via playwright if TLS Client fails during the handshake."""

import time
import json
import os

from playwright.sync_api import sync_playwright

from base import logger, proxy_map
from namings import QUERY_DETAILS_MAP


class BrowserSession:
    """
    Creates browser session, fetches request signature and saves to json file.

    That signature can be used with tls client requests.
    """

    GRAPHQL_BACKEND_API_URL = "https://opensea.io/__api/graphql/"

    def __init__(self, request_name: str, timeout: int = 5000):
        self.request_name = request_name
        self.timeout = timeout

    def run(self):
        """Runner function."""

        with sync_playwright() as p:
            proxy_parts = proxy_map["https"].split("://")[1].split("@")
            proxy_credentials = proxy_parts[0]  # username:password
            proxy_server = proxy_parts[1]  # host:port
            username, password = proxy_credentials.split(":")
            server = f"https://{proxy_server}"

            browser = p.chromium.launch(
                proxy={
                    "server": server,  # Proxy server address
                    "username": username,  # Proxy username
                    "password": password  # Proxy password
                },
                args=[
                    "--headless=new",
                    "--disable-gpu",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-blink-features=AutomationControlled",
                    "--remote-debugging-port=9222"
                ]
            )
            context = browser.new_context(
                java_script_enabled=True,
                record_har_path="network.har",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            )
            page = context.new_page()

            # Register handlers simultaneously
            page_url = QUERY_DETAILS_MAP[self.request_name]["accessor_page_url"]
            page.route("**/__api/graphql/**", lambda route, request: self._handle_route(route, request, context, self.request_name))
            page.goto(page_url, wait_until="domcontentloaded")
            time.sleep(1)

            page.wait_for_timeout(self.timeout)  # Wait for network activity

            logger.info("Timeout reached, closing browser...")
            context.close()
            browser.close()

    def _handle_route(self, route, request, context, request_key):
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
            else:
                route.continue_()
        else:
            route.continue_()

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
