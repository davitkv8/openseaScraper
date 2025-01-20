import json

import requests
import tls_client

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
