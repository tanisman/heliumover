from cmath import log
import math
from operator import truediv
import queue
import socket
import threading
import logging
import random
import json
from base64 import b64decode
from base58 import b58encode
import helium_api
from proxy_config import GATEWAY_UID, HELIUM_PUBKEY


class lora_client():
    def __init__(self, host, port, downstream) -> None:
        succ, hotspot = helium_api.get_hostspot(HELIUM_PUBKEY)
        while not succ:
            logging.warning("[lora_client] api request failed (self), retrying...")
            succ, hotspot = helium_api.get_hostspot(HELIUM_PUBKEY)
        self.hotspot = hotspot["data"]
        logging.info(f"[lora_client] hotspot: {self.hotspot['address']} (lat={self.hotspot['lat']}, lng={self.hotspot['lng']})")

        connected = False

        while not connected:
            try:
                self.sock_up = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock_up.settimeout(0.1) # 100ms
                self.sock_up.connect((host, port))

                self.sock_down = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock_down.settimeout(0.2) # 200ms
                self.sock_down.connect((host, port))
                connected = True
                logging.info("[lora_client] connected")
            except Exception as e:
                logging.error(f"[lora_client] failed to connect to {host}:{port}")

        self.downstream = downstream
        self.upstream_queue = queue.Queue()
        self.downstream_queue = queue.Queue()
        self.tx_count = 0
        self.mutex = threading.Lock()
        self.thread_up = threading.Thread(target=self.worker_up)
        self.thread_up.daemon = True
        self.thread_down = threading.Thread(target=self.worker_down)
        self.thread_down.daemon = True
        self.known_hotspots = dict()
        self.tx_tokens = dict()

    def __del__(self):
        self.thread_up.raise_error()
        self.thread_down.raise_error()
        
    def deserialize_lora(self, msg):
        ver = msg[0]
        token = msg[1:3]
        identifier = msg[3]
        return ver, token, identifier

    def enqueue_push_data(self, msg):
        logging.debug("[lora_client] enqueue_push_data")
        push_data_msg = json.loads(msg)
        payload = b64decode(push_data_msg["data"])
        pubkey = b58encode(payload[2:2+33]).decode('utf-8')

        if pubkey not in self.known_hotspots:
            succ, json = helium_api.get_hostspot(pubkey)
            while not succ:
                logging.warning("[lora_client] api request failed, retrying...")
                succ, json = helium_api.get_hostspot(pubkey)
            
            self.known_hotspots[pubkey] = json["data"]
        
        lng = self.known_hotspots[pubkey]["lng"]
        lat = self.known_hotspots[pubkey]["lat"]

        R = 6371e3 # metres
        x1 = lat * (math.pi/180)
        x2 = self.hotspot["lat"] * (math.pi/180)
        dx = (self.hotspot["lat"] - lat) * (math.pi/180)
        dy = (self.hotspot["lng"] - lng) * (math.pi/180)

        a = math.sin(dx/2) * math.sin(dx/2) + math.cos(x1) * math.cos(x2) * math.sin(dy/2) * math.sin(dy/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        d = R * c
        # NOTE: Transmit gain is set to 0 when calculating free_space_path_loss
        # This is because the packet forwarder will be configured to subtract the antenna
        # gain and miner will always transmit at region EIRP.
        path_loss = 20 * math.log10(d) + 20 * math.log10(push_data_msg["freq"] * 10 ** 6) - 147.55 - 0 - self.known_hotspots["gain"] / 10
        
        # randomize RSSI value
        path_loss += random.randint(-30, -1)
        
        # update rssi value in push_data_msg
        push_data_msg["rssi"] = path_loss

        self.upstream_queue.put(
            bytes([2, random.randint(0, 255), random.randint(0, 255), 0]) 
            + bytes.fromhex(GATEWAY_UID) 
            + json.dumps(push_data_msg).encode("utf-8"))


    def enqueue_pull_data(self):
        logging.debug("[lora_client] enqueue_pull_data")
        self.downstream_queue.put(bytes([2, random.randint(0, 255), random.randint(0, 255), 2]) + bytes.fromhex(GATEWAY_UID))

    def enqueue_tx_ack(self, msg, data_hash):
        logging.debug("[lora_client] enqueue_tx_ack")
        token = self.tx_tokens[data_hash]
        del self.tx_tokens[data_hash]
        payload = bytes([2]) + token + bytes([5]) + bytes.fromhex(GATEWAY_UID)
        if msg is not None:
            payload = payload + msg.encode("utf-8")
        self.downstream_queue.put(payload)

    def process_pull_resp(self, client, token, msg):
        gateway_id = msg[4:12]
        json_object = msg[12:].decode('utf-8')
        logging.debug(f"[lora_client] PULL_RESP received from {client}: {json_object}")
        
        self.mutex.acquire()
        try:
            self.tx_count += 1
        finally:
            self.mutex.release()

        pull_data_msg = json.loads(json_object)
        self.tx_tokens[hash(pull_data_msg["txpk"]["data"])] = token

        self.downstream(json_object)

    def on_tx_ack(self, data_hash, msg):
        self.mutex.acquire()
        try:
            if self.tx_count > 0:
                self.tx_count -= 1
                self.enqueue_tx_ack(msg, data_hash)
        finally:
            self.mutex.release()

    def worker_up(self):
        while True:
            # this only sends PUSH_DATA to miner
            try:
                msg = self.upstream_queue.get(block=True, timeout=1)
                self.sock_up.send(msg)
            except queue.Empty:
                pass
            
            # this only receives PUSH_ACK from miner and ignores it
            try:
                msg = self.sock_up.recv(4096)
                if len(msg) < 4:
                    logging.error(f"[lora_client:worker_up] message too short: {msg}")
                    continue

                ver, token, identifier = self.deserialize_lora(msg)

                if ver != 2:
                    logging.error(f"[lora_client:worker_up] unknown protocol version {ver}")
                    continue
                
                if identifier != 1:
                    logging.error(f"[lora_client:worker_up] unknown identifier {identifier}")
                    continue

            except socket.timeout as e:
                continue

    def worker_down(self):
        while True:
            # this sends PULL_DATA and TX_ACK to miner (txack only to beacon owner)
            try:
                msg = self.downstream_queue.get(block=True, timeout=1)
                self.sock_down.send(msg)
            except queue.Empty:
                pass
            
            # this receives PULL_ACK and PULL_RESP from miner
            try:
                msg = self.sock_up.recv(4096)
                if len(msg) < 4:
                    logging.error(f"[lora_client:worker_down] message too short: {msg}")
                    continue

                ver, token, identifier = self.deserialize_lora(msg)

                if ver != 2:
                    logging.error(f"[lora_client:worker_down] unknown protocol version {ver}")
                    continue

                if identifier == 4: # PULL_ACK
                    pass # ignore
                elif identifier == 3: # PULL_RESP
                    self.process_pull_resp(self.sock_up, token, msg)
            except socket.timeout as e:
                continue


    def start(self):
        self.thread_up.start()
        self.thread_down.start()

