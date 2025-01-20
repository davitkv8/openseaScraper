# OpeanSea Scraper App

# About project
```
    Project idea is to scrap OpenSea.com in more advanced way.
    I've seen different implementations but mostly they were highly depended on mimic browser tools like Selenium/Playwright.
    
    In my own implementation I'm trying to avoid using mimic browser tools as per request as much as possible.
    So, instead of just directly (pseudo code) playwright.open("opensea.com") -> give me content -> and parse it,
    In this code prioritizing to be able to just directly gain the data through Graphql backend API which is cloudflare protected.
```


# Infrastructure
```
    Currently there is no anything special with the project infrastructure itself,
    but what it is is that I have divided scraper.py and browser_session.py modules.
    
    1) browser_session module only runs at the initial stage, it's idea is to get and save request signature it's details.
    after browser_session stores specific request query, it's ready to go for a very long time, 
    (while cookies will not expire for example or cloudflare anti-bot do not mark signature as invalid) 
    but I have not included last part logic into the implementation yet.
    
    2) scraper.py module - this module makes requests to Opensea's Graphql backends.
    It uses TLS Client + request details gained from the browser_session.
    why this way? - so, I've seen that by average TLS Client has a pretty good results bypassing cloudflare protection,
    but sometimes even when the "PERFECT HANDHSAKE" is made, there is a chance that cloudflare turnstile will block the process, 
    for example cloudflare require additional checks, or block it for X amount of time. 
    So, that reason, if we have request details, dynamic tokens and cookies extracted from REAL browsing session (from browser_session),
    and we will initialize it with TLS - there is SUPER HIGH chance of success.
    
    So, scraper.py module runs and gets the data from cloudflare turnstile protected Graphql API just directly.
```


# Ideas
```
    The most desired implementation for me would be to fully get rid of mimic browsers
     - for this I have found somethig really interesting - https://github.com/LOBYXLYX/Cloudflare-Bypass
    Extracting dynamic cf_clearance from the request, but is it enough all the time ? 
    there is some more experiments needed to make a conclujion about dropping mimic browsers fully. 
```

# How to run
```
    1) pip install -r requirements.txt
    2) python main.py
```
