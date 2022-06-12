import requests

API_URL = "https://helium-api.stakejoy.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    
def get_hostspot(pubkey):
    r = requests.get(f"{API_URL}/v1/hotspots/{pubkey}", headers={"User-Agent": USER_AGENT})
    return r.status_code == 200, r.json() if r.status_code == 200 else None
