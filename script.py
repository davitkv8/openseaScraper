import json

import requests
import tls_client
from playwright.sync_api import sync_playwright

from namings import QUERY_DETAILS_MAP
from base import proxy_map

session = tls_client.Session(
    client_identifier="chrome_112",  # Mimics Chrome v112
    random_tls_extension_order=True,  # Randomize TLS extension order
)

session.proxies = proxy_map


url = 'https://opensea.io/__api/graphql/'

# with open("saved_request.json") as f:
#     saved_request = json.load(f)["TOP_RANKINGS"]
#
# method = saved_request["method"]
# headers = saved_request["headers"]
# cookies = {cookie["name"]: cookie["value"] for cookie in saved_request["cookies"]}
# request_body = QUERY_DETAILS_MAP["TOP_RANKINGS"]["body"]
#
#
# result = session.post(
#     url,
#     headers=headers,
#     # cookies=cookies,
#     json=request_body,
# )
#
# print(result.status_code)
# print(result.text)

# Make a request
response = session.get("https://ip.oxylabs.io/location")
response_2 = requests.get("https://ip.oxylabs.io/location", proxies=proxy_map)
print("Response:", response.text)
print("Response:", response_2.text)


print(proxy_map)

with sync_playwright() as p:

    proxy_parts = proxy_map["https"].split("://")[1].split("@")
    proxy_credentials = proxy_parts[0]  # username:password
    proxy_server = proxy_parts[1]  # host:port

    username, password = proxy_credentials.split(":")
    server = f"https://{proxy_server}"

    browser = p.chromium.launch(
        proxy={
            "server": server,     # Proxy server address
            "username": username, # Proxy username
            "password": password  # Proxy password
        }
    )
    context = browser.new_context()
    page = context.new_page()

    page.wait_for_timeout(10000)

    # Navigate to a test site to verify the proxy
    page.goto("https://ip.oxylabs.io/location")
    print("Playwright Proxy Page Content:", page.content())

    browser.close()
