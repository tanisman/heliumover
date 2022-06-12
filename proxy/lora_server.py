import socket
import threading
import logging
import json
import random
import helium_api
import timer

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
        if "rxpk" in push_data_msg:
            for rxpk in push_data_msg["rxpk"]:
                # longfi header (3bytes) + longfi oui(7bit encoded) + longfi did (7bit encoded) + longfi fp (4bytes) + longfi seq(7bit encoded) + longfi data (variable)
                # longfi data for helium msg is IV (2bytes) + OnionCompactKey(33bytes) + Tag (4bytes) + CipherText (variable)
                msg = helium_api.decrypt_radio(rxpk["data"])
                if msg is not None:
                    if msg.header.oui == 0 and msg.header.did == 1:
                        logging.info(f"[lora_server] got helium beacon poc_id={msg.poc_id} (oui={msg.header.oui} did={msg.header.did}) payload len={len(msg.ciphertext)}")
                    else:
                        logging.info(f"[lora_server] maybe got helium beacon poc_id={msg.poc_id} (oui={msg.header.oui} did={msg.header.did}) payload len={len(msg.ciphertext)}")
                    rxpk["receiver_address"] = helium_api.MY_HOTSPOT['address']
                    rxpk["receiver_lat"] = helium_api.MY_HOTSPOT['lat']
                    rxpk["receiver_lng"] = helium_api.MY_HOTSPOT['lng']
                    rxpk["receiver_gain"] = helium_api.MY_HOTSPOT["gain"]
                    self.upstream(rxpk)
        else:
            self.upstream(push_data_msg)

    def process_pull_data(self, client, token, msg):
        logging.debug(f"[lora_server] PULL_DATA received from {client}")
        # send PULL_ACK
        self.sock.sendto(bytes([2, token[0], token[1], 4]), client) # to gateway (sending in behalf of the miner)        
        msgs_to_send = self.pull()
        for index, lora_msg in enumerate(msgs_to_send):
            msg = json.loads(lora_msg)
            send_tok = bytes([random.randint(0, 255), random.randint(0, 255)])
            self.tx_tokens[hash(send_tok)] = hash(msg["txpk"]["data"])
            msg["txpk"]["imme"] = True

            # delete custom transmitter field used for poc spoofing
            del msg["transmitter"]

            timer.add_timer(
                5 + index, 
                lambda pair : self.sock.sendto(pair[0], pair[1]), 
                [bytes([2]) + send_tok + bytes([3]) + json.dumps(msg).encode('utf-8'), client])

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

            self.tx_ack(sent_data_hash, tx_ack_msg)
        else:
            logging.debug(f"[lora_server] TX_ACK received from {client}")
            self.tx_ack(sent_data_hash, None)
    
    def worker(self):
        while True:
            try:
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
            except Exception as e:
                logging.error(f"[lora_server:worker] exception: {e}")
                continue        

    def start(self):
        self.thread.start()
            

