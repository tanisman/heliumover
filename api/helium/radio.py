from hashlib import sha256
from base64 import b64encode, b64decode
import helium.longfi as longfi
import math

class radio_pkt():
    def __init__(self, header, iv, onion_compact_key, tag, ciphertext):
        self.flag = onion_compact_key[0]
        self.is_compact = self.flag & 0x0F
        self.network_id = self.flag >> 4
        self.header = header
        self.iv = iv
        self.poc_id = b64encode(sha256(onion_compact_key).digest()).decode('utf-8')
        self.tag = tag
        self.ciphertext = ciphertext

def decrypt_radio(b64pkt):
    longfi_pkt = b64decode(b64pkt)
    header, payload, longfi_size = longfi.decode(longfi_pkt)
    if len(longfi_pkt) >= 3 + 2 + 33 + 4:
        if len(payload) >= 2  + 33 + 4:
            return radio_pkt(header, payload[:2], payload[2:2+33], payload[2+33:2+33+4], payload[2+33+4:])
    return None

def fspl(self, lat1, lng1, lat2, lng2, freq, gain, extra_d = 0):
    R = 6371e3 # metres
    x1 = lat1 * (math.pi/180)
    x2 = lat2 * (math.pi/180)
    dx = (lat2 - lat1) * (math.pi/180)
    dy = (lng2 - lng1) * (math.pi/180)

    a = math.sin(dx/2) * math.sin(dx/2) + math.cos(x1) * math.cos(x2) * math.sin(dy/2) * math.sin(dy/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c + extra_d
    # (helim/miner) NOTE: Transmit gain is set to 0 when calculating free_space_path_loss
    # This is because the packet forwarder will be configured to subtract the antenna
    # gain and miner will always transmit at region EIRP.
    path_loss = 20 * math.log10(d) + 20 * math.log10(freq) - 147.55 - 0 - gain
        
    return path_loss * -1

def freq_channel(freq):
    freq = round(freq, 1)
    return {
        "868.1": 0,
        "868.3": 1,
        "868.5": 2,
        "867.1": 3,
        "867.3": 4,
        "867.5": 5,
        "867.7": 6,
        "867.9": 7,
    }[str(freq)]

