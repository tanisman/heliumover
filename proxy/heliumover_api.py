import requests
import time
from proxy_config import HELIUMOVER_API_UPSTREAM, HELIUMOVER_API_DOWNSTREAM, HELIUMOVER_API_HOTSPOT, HELIUMOVER_API_KEY

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"

def update_hotspot(pubkey, lat, lng, gain):
    try:
        r = requests.post(
            f"{HELIUMOVER_API_HOTSPOT}/{pubkey}", 
            headers={"User-Agent": USER_AGENT, "X-API-Key": HELIUMOVER_API_KEY},
            json={
                "lat": lat,
                "lng": lng,
                "gain": gain
            })
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"exception": e}
    
def post_upstream(pubkey, push_data_msg):
    try:
        r = requests.post(
            f"{HELIUMOVER_API_UPSTREAM}/{pubkey}", 
            headers={"User-Agent": USER_AGENT, "X-API-Key": HELIUMOVER_API_KEY},
            json=push_data_msg)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"exception": e}

def post_downstream(pubkey, pull_data_msg):
    try:
        r = requests.post(
            f"{HELIUMOVER_API_DOWNSTREAM}/{pubkey}", 
            headers={"User-Agent": USER_AGENT, "X-API-Key": HELIUMOVER_API_KEY},
            json=pull_data_msg)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"exception": e}


def get_upstream(pubkey):
    try:
        r = requests.get(
            f"{HELIUMOVER_API_UPSTREAM}/{pubkey}", 
            headers={"User-Agent": USER_AGENT, "X-API-Key": HELIUMOVER_API_KEY})
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"exception": e}