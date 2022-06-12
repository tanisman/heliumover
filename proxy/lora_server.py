import socket
import threading
import logging
import json
import random
from base64 import b64decode
from base58 import b58encode


class lora_server():
    def __init__(self, host, port, upstream, pull, tx_ack) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.upstream = upstream
        self.pull = pull
        self.tx_ack = tx_ack
        self.thread = threading.Thread(target=self.worker)
        self.thread.daemon = True
        self.tx_tokens = dict()

    def __del__(self):
        self.thread.raise_error()

    def deserialize_lora(self, msg):
        ver = msg[0]
        token = msg[1:3]
        identifier = msg[3]
        return ver, token, identifier

    def process_push_data(self, client, token, msg):
        gateway_id = msg[4:12]
        json_object = msg[12:].decode('utf-8')
        logging.debug(f"[lora_server] PUSH_DATA received from {client}: {json_object}")
        # send PUSH_ACK
        self.sock.sendto(bytes([2, token[0], token[1], 1]), client) # to gateway (sending in behalf of the miner)

        push_data_msg = json.loads(json_object)
        for rxpk in push_data_msg["rxpk"]:
            payload = b64decode(rxpk["data"])
            if len(payload) >= 2 + 33 + 4:
                pubkey = b58encode(payload[2:2+33]).decode('utf-8')
                logging.debug(f"[lora_server] got helium beacon from {pubkey}")
                self.upstream(rxpk)

    def process_pull_data(self, client, token, msg):
        logging.debug(f"[lora_server] PULL_DATA received from {client}")
        # send PULL_ACK
        self.sock.sendto(bytes([2, token[0], token[1], 4]), client) # to gateway (sending in behalf of the miner)        
        msgs_to_send = self.pull()
        for lora_msg in msgs_to_send:
            send_tok = bytes([random.randint(0, 255), random.randint(0, 255)])
            self.tx_tokens[hash(send_tok)] = hash(json.loads(lora_msg)["txpk"]["data"])
            
            self.sock.sendto(
                bytes([2]) + send_tok + bytes([3]) + lora_msg.encode('utf-8'), 
                client)

    def process_tx_ack(self, client, token, msg):
        gateway_id = msg[4:12]
        sent_data_hash = self.tx_tokens[hash(token)]
        del self.tx_tokens[hash(token)]

        if len(msg) > 12:
            json_object = msg[12:].decode('utf-8')
            logging.debug(f"[lora_server] TX_ACK received from {client}: {json_object}")
            tx_ack_msg = json.loads(json_object)
            
            if "txpk_ack" in tx_ack_msg:
                if "error" in tx_ack_msg["txpk_ack"]:
                    logging.error(f"[lora_server] TX_ACK error {tx_ack_msg['txpk_ack']['error']}")

            self.tx_ack(sent_data_hash, json_object)
        else:
            logging.debug(f"[lora_server] TX_ACK received from {client}")
            self.tx_ack(sent_data_hash, None)
    
    def worker(self):
        while True:
            msg, client = self.sock.recvfrom(4096)
            if len(msg) < 4:
                logging.error(f"[lora_server] message too short: {msg}")
                continue

            ver, token, identifier = self.deserialize_lora(msg)

            if ver != 2:
                logging.error(f"[lora_server] unknown protocol version {ver}")
                continue

            if identifier == 0: # PUSH_DATA (upstream initiator)
                self.process_push_data(client, token, msg)
            elif identifier == 2: # PULL_DATA (downstream initiator)
                self.process_pull_data(client, token, msg)
            elif identifier == 5: # TX_ACK
                self.process_tx_ack(client, token, msg)


    def start(self):
        self.thread.start()
            

