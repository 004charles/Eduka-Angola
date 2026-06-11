import urllib.request

urls = [
    "https://www.edukangola.com/static/manifest.json",
    "https://www.edukangola.com/static/assets/images/icons/pwa-192x192.png",
    "https://www.edukangola.com/sw.js"
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        print(f"{url} -> {response.getcode()}")
    except Exception as e:
        print(f"{url} -> {e}")
