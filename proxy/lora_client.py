import queue
import socket
import threading
import logging
import random
import json
from proxy_config import GATEWAY_UID


class lora_client():
    def __init__(self, host, port, downstream) -> None:
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

        self.upstream_queue = queue.Queue()
        self.downstream_queue = queue.Queue()
        self.tx_count = 0
        self.mutex = threading.Lock()
        self.thread_up = threading.Thread(target=self.worker_up)
        self.thread_up.daemon = True
        self.thread_down = threading.Thread(target=self.worker_down)
        self.thread_down.daemon = True
        self.tx_tokens = dict()
        self.downstream = downstream

    def __del__(self):
        self.thread_up.raise_error()
        self.thread_down.raise_error()
        
    def deserialize_lora(self, msg):
        ver = msg[0]
        token = msg[1:3]
        identifier = msg[3]
        return ver, token, identifier

    def enqueue_upstream_msg(self, msg):
        self.upstream_queue.put(
            bytes([2, random.randint(0, 255), random.randint(0, 255), 0]) 
            + bytes.fromhex(GATEWAY_UID) 
            + msg.encode("utf-8"))

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

        self.downstream(pull_data_msg)

    def on_tx_ack(self, data_hash, msg):
        self.mutex.acquire()
        try:
            if self.tx_count > 0:
                self.tx_count -= 1
                self.enqueue_tx_ack(json.dumps(msg) if msg is not None else None, data_hash)
        finally:
            self.mutex.release()

    def worker_up(self):
        while True:
            # this only sends PUSH_DATA to miner
            try:
                msg = self.upstream_queue.get(block=True, timeout=1)
                self.sock_up.send(msg)
                logging.debug(f"[lora_client:worker_up] sent: {msg}")
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
            except socket.timeout as ste:
                continue
            except Exception as e:
                logging.error(f"[lora_client:worker_up] exception: {e}")
                continue

    def worker_down(self):
        while True:
            # this sends PULL_DATA and TX_ACK to miner (txack only to beacon owner)
            try:
                msg = self.downstream_queue.get(block=True, timeout=1)
                self.sock_down.send(msg)
                logging.debug(f"[lora_client:worder_down] sent: {msg}")
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
            except socket.timeout as ste:
                continue
            except Exception as e:
                logging.error(f"[lora_client:worker_down] {e}")
                continue

    def start(self):
        self.thread_up.start()
        self.thread_down.start()

