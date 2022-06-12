import requests
import time
from hashlib import sha256
from base58 import b58encode
from base64 import b64encode, b64decode
import longfi

class helium_radio_pkt():
    def __init__(self, header, iv, onion_compact_key, tag, ciphertext):
        self.flag = onion_compact_key[0]
        self.is_compact = self.flag & 0x0F
        self.network_id = self.flag >> 4
        self.header = header
        self.iv = iv
        self.poc_id = b64encode(sha256(onion_compact_key).digest()).decode('utf-8')
        self.tag = tag
        self.ciphertext = ciphertext

API_URL = "https://helium-api.stakejoy.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
MY_HOTSPOT = None

def gethotspot(pubkey):
    try:
        r = requests.get(f"{API_URL}/v1/hotspots/{pubkey}", headers={"User-Agent": USER_AGENT})
        return r.status_code, r.json() if r.status_code == 200 else None
    except:
        time.sleep(5)
        return 500, None

def bin_to_pubkey(bin):
    vpayload = bytes([0]) + bin
    checksum = sha256(sha256(vpayload).digest()).digest()[:4]
    return b58encode(vpayload + checksum).decode('utf-8')

def decrypt_radio(b64pkt):
    longfi_pkt = b64decode(b64pkt)
    header, payload, longfi_size = longfi.decode(longfi_pkt)
    if len(longfi_pkt) >= 3 + 2 + 33 + 4:
        if len(payload) >= 2  + 33 + 4:
            return helium_radio_pkt(header, payload[:2], payload[2:2+33], payload[2+33:2+33+4], payload[2+33+4:])
    return None