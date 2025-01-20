"""This module generates and stores all essential request details via playwright if TLS Client fails during the handshake."""
import threading
import json
import os

from playwright.sync_api import sync_playwright

from base import ProxyService, logger
from namings import QUERY_DETAILS_MAP, AvailableQueries


class BrowserSession:
    """
    Creates browser session, fetches request signature and saves to json file.

    That signature can be used with tls client requests.
    """

    # Attributes
    GRAPHQL_BACKEND_API_URL = "https://opensea.io/__api/graphql/"

    # Services
    proxy_service = ProxyService()

    def __init__(self, request_names: AvailableQueries, timeout: int = 5000):
        self.request_names = request_names
        self.timeout = timeout


    def handle_route(self, route, request, context, request_key, proxy_map):
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
                    "proxy_map": proxy_map,
                }

                self._save_request_details(request_key, saved_request)

                # Modify the payload (if needed) | I'm leaving it as a comment, as it is some different kind of implementation idea for me.
                # modified_payload = json.loads(post_data)
                # modified_payload["variables"]["timeWindow"] = "ALL_TIME"
                # modified_payload["variables"]["count"] = 100
            else:
                route.continue_()
        else:
            route.continue_()

    def _process_request(self, proxy_map, request_name):
        with sync_playwright() as p:
            https_proxy = proxy_map["https"]
            proxy_parts = https_proxy.split("://")[1].split("@")
            proxy_credentials = proxy_parts[0]  # username:password
            proxy_server = proxy_parts[1]  # host:port
            username, password = proxy_credentials.split(":")
            server = f"https://{proxy_server}"

            try:
                logger.info(f"PROCESSING WITH {server}, {username}, {QUERY_DETAILS_MAP[request_name]["accessor_page_url"]}")
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
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
                )
                page = context.new_page()

                # Register handler for this request
                page_url = QUERY_DETAILS_MAP[request_name]["accessor_page_url"]
                page.route("**/__api/graphql/**", lambda route, request: self.handle_route(route, request, context, request_name, proxy_map))

                # Load the page
                page.goto(page_url, wait_until="domcontentloaded")

                # Wait for network load
                page.wait_for_timeout(timeout=self.timeout)

                logger.info(f"Request {request_name} processed successfully.")
            except Exception as e:
                logger.error(f"Error processing request {request_name} with proxy {https_proxy}: {e}")
            finally:
                context.close()
                browser.close()

    def run(self):
        threads = []
        for session_id, request_name in enumerate(self.request_names):
            proxy_map = self.proxy_service.generate_proxy(session_id + 1)  # Just avoiding session 0
            # self._process_request(proxy_map["https"], request_name)

            thread = threading.Thread(target=self._process_request, args=(proxy_map, request_name))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        logger.info("All requests processed.")


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
