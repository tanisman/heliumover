from time import sleep
from proxy_config import *
from lora_server import lora_server
from lora_client import lora_client
from threading import Lock
import logging
import json
import helium_api
import heliumover_api

downstream_client = None
upstream_server = None
mutex = Lock()
downstream_queue = []

def lora_upstream(json_object):
    if "data" in json_object:
        http_status, respose = heliumover_api.post_upstream(helium_api.MY_HOTSPOT["address"], json_object)
        if http_status != 200:
            logging.warning(f"[heliumover] post upstream returned {http_status} ({respose})")
        downstream_client.enqueue_upstream_msg(json.dumps({"rxpk": [json_object]}))
    else:
        downstream_client.enqueue_upstream_msg(json.dumps(json_object))

def lora_downstream(json_object):
    global mutex
    global downstream_queue

    http_status, response = heliumover_api.post_downstream(helium_api.MY_HOTSPOT["address"], json_object["txpk"])
    if http_status != 200:
        logging.warning(f"[heliumover] post downstream returned {http_status} ({response})")
        
    mutex.acquire()
    try:
        downstream_queue.append(json_object)
    finally:
        mutex.release()

def lora_pull():
    global mutex
    global downstream_queue
    downstream_client.enqueue_pull_data()
    mutex.acquire()
    try:    
        q = downstream_queue.copy()
        downstream_queue.clear()
        return q
    finally:
        mutex.release()

def main():
    logging.basicConfig(level=logging.DEBUG)
    global downstream_client
    global upstream_server

    status, hotspot = helium_api.gethotspot(HELIUM_PUBKEY)
    while status != 200:
        if status == 404:
            raise Exception("NOT ONBOARDED DEVICE!!!")
        logging.warning("[lora_client] api request failed (self), retrying...")
        status, hotspot = helium_api.gethotspot(HELIUM_PUBKEY)
    helium_api.MY_HOTSPOT = hotspot["data"]
    logging.info(f"[{GATEWAY_UID}] Running Hotspot: {helium_api.MY_HOTSPOT['address']} (lat={helium_api.MY_HOTSPOT['lat']}, lng={helium_api.MY_HOTSPOT['lng']})")
    
    status, response = heliumover_api.update_hotspot(helium_api.MY_HOTSPOT["address"], helium_api.MY_HOTSPOT["lat"], helium_api.MY_HOTSPOT["lng"], helium_api.MY_HOTSPOT["gain"])
    if status != 200:
        logging.error(f"[heliumover] update_hotspot returned {status} ({response})")

    # PROXY <-> MINER
    downstream_client = lora_client(
        MINER_HOST, 
        MINER_PORT, 
        lora_downstream) 
    downstream_client.start()

    # LGW <-> PROXY
    upstream_server = lora_server(
        PROXY_HOST, 
        PROXY_PORT, 
        lora_upstream, 
        lora_pull,
        lambda x, y : downstream_client.on_tx_ack(x, y))
    upstream_server.start()

    while True:
        sleep(5)
        try:
            http_status, response = heliumover_api.get_upstream(helium_api.MY_HOTSPOT["address"])
            if http_status != 200:
                logging.warning(f"[heliumover] get upstream returned {http_status} ({response})")
                continue
            if len(response["rxpk"]) > 0:
                downstream_client.enqueue_upstream_msg(json.dumps(response))
        except Exception as e:
            logging.warning(f"[heliumover] get upstream failed: {e}")
            continue

if __name__ == "__main__":
    main()