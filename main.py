

from playwright.sync_api import sync_playwright
import json
import sys


# Function to intercept and modify the targeted request
def handle_route(route, request, context):
    if request.url == "https://opensea.io/__api/graphql/" and request.method == "POST":
        post_data = request.post_data
        if post_data and "RankingsPageTopQuery" in post_data:
            print("REQUEST FOUND")
            print("\n=== Intercepted Targeted Request ===")
            print("Original Payload:", json.dumps(json.loads(post_data), indent=2))

            # Save all request details
            saved_request = {
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "cookies": context.cookies(),  # Save cookies from the browser context
                "post_data": json.loads(post_data),
            }

            # Save the details to a file
            with open("saved_request.json", "w") as file:
                json.dump(saved_request, file, indent=2)

            # Modify the payload (if needed)
            modified_payload = json.loads(post_data)
            modified_payload["variables"]["timeWindow"] = "ALL_TIME"
            modified_payload["variables"]["count"] = 100

            print("\n=== Modified Payload ===")
            print(json.dumps(modified_payload, indent=2))

            # Continue the request with the modified payload
            sys.exit()
            route.continue_(post_data=json.dumps(modified_payload))
        else:
            route.continue_()
    else:
        route.continue_()



# Function to handle the response and ensure it's the one we're targeting
def handle_response(response, browser):
    if response.url == "https://opensea.io/__api/graphql/":
        try:
            data = response.json()
            print(f"RESP IS {data.get('data')}")
            if data.get("data") and "topCollectionsByCategory" in data["data"]:  # Assuming we care about the "data" field in the response ##### and "RankingsPageTopQuery" in data["data"]
                print("RESPONSE FOUND")
                print("\n=== Targeted GraphQL Response Detected ===")
                print(json.dumps(data, indent=2))

                # Save to file for debugging
                with open("target_response.json", "w") as file:
                    json.dump(data, file, indent=2)

                # Exit the process
                print("Desired response received. Exiting...")
                # browser.close()
                # sys.exit(0)
        except Exception as e:
            print(f"Error processing response: {e}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Intercept requests to modify the payload
        page.route("**/__api/graphql/**", lambda route, request: handle_route(route, request, context))

        # Attach response listener
        page.on("response", lambda response: handle_response(response, browser))

        # Navigate to the page
        page.goto("https://opensea.io/rankings?sortBy=total_volume")
        page.wait_for_timeout(10000)  # Wait for network activity for 10 seconds

        print("Timeout reached. Closing browser...")
        browser.close()


if __name__ == "__main__":
    main()
