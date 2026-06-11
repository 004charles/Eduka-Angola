import urllib.request
import json
import re

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            print(f"--- {url} ---")
            print(f"Status: {response.getcode()}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            # Print first 200 chars to verify content
            print(content[:200] + "...\n")
            return content
    except Exception as e:
        print(f"--- {url} ---")
        print(f"ERROR: {e}\n")
        return None

html = check_url("https://www.edukangola.com/")
manifest = check_url("https://www.edukangola.com/static/manifest.json")
sw = check_url("https://www.edukangola.com/sw.js")

if html:
    if "pwa-install-banner" in html:
        print("SUCCESS: pwa-install-banner found in HTML")
    else:
        print("FAILURE: pwa-install-banner NOT FOUND in HTML")
        
    if "manifest.json" in html:
        print("SUCCESS: manifest.json link found in HTML")
    else:
        print("FAILURE: manifest.json link NOT FOUND in HTML")
