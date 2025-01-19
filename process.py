import tls_client
import json
import requests

# Load the saved request details
with open("saved_request.json", "r") as file:
    saved_request = json.load(file)

# Extract details from the saved request
url = saved_request["url"]
method = saved_request["method"]
headers = saved_request["headers"]
cookies = {cookie["name"]: cookie["value"] for cookie in saved_request["cookies"]}
post_data = saved_request.get("post_data")

print(cookies)

# Create a TLS client session
session = tls_client.Session(
    client_identifier="chrome_112",  # Mimics Chrome v112
    random_tls_extension_order=True,  # Randomize TLS extension order
)

# Make the request based on the saved method
if method == "POST":
    response = session.post(
        url,
        headers=headers,
        cookies=cookies,
        json=post_data,
    )
elif method == "GET":
    response = session.get(
        url,
        headers=headers,
        # cookies=cookies,
    )
else:
    print(f"Unsupported method: {method}")
    exit()


# Print the response
print("\n=== Response ===")
print("Status Code:", response.status_code)
try:
    data = response.json()
    print("Response JSON:", data)
    print(f"Len {data['data']['topCollectionsByCategory']['edges'].__len__()}")
except json.JSONDecodeError:
    print("Response Text:", response.text)



