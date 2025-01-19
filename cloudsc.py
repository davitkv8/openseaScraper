import requests

from aqua import CF_Solver


cf = CF_Solver('https://opensea.io')
cookie = cf.cookie()

print(cookie)

# Use the captured cf_clearance token
cookies = {
    "cf_clearance": cookie
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
}

# Make a request with the token
response = requests.get("https://opensea.io/", cookies=cookies, headers=headers)

print(response.status_code)
print(response.text)
