class header():
    """
    LongFi header
    """
    def __init__(self, hdr, oui, did, fingerprint, seq):
        self.hdr = hdr
        self.oui = oui
        self.did = did
        self.fingerprint = fingerprint
        self.seq = seq

def encode_to_7bit(value):
    """
    Encode unsigned int to 7-bit str data
    """
    data = bytearray()
    number = abs(value)
    while number >= 0x80:
        data.append((number | 0x80) & 0xff)
        number >>= 7
    data.append(number & 0xff)
    return bytes(data)

def decode_from_7bit(data):
    """
    Decode 7-bit encoded int from str data
    """
    result = 0
    size = 0
    for index, byte in enumerate(data):
        result |= (byte & 0x7f) << (index * 7)
        size += 1
        if byte & 0x80 == 0:
            break
    return result, size
    
def decode(data):
    hdr = data[:3]
    oui, size_oui = decode_from_7bit(data[3:])
    did, size_did = decode_from_7bit(data[3+size_oui:])
    fingerprint = data[3+size_oui+size_did:3+size_oui+size_did+4]
    seq, size_seq = decode_from_7bit(data[3+size_oui+size_did+4:])
    payload = data[3+size_oui+size_did+4+size_seq:]

    return header(hdr, oui, did, fingerprint, seq), payload, 3+size_oui+size_did+4+size_seq
