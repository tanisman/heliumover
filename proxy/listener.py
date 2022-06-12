from time import sleep
from proxy_config import *
from mqtt_client import mqtt_client
from lora_server import lora_server
from lora_client import lora_client
from threading import Lock
import logging
import json
import helium_api

mqtt = None
downstream_client = None
upstream_server = None
mutex = Lock()
downstream_queue = []

def mqtt_upstream(msg):
    global downstream_client
    downstream_client.enqueue_push_data(msg)

def mqtt_downstream(msg):
    global mutex
    global downstream_queue
    mutex.acquire()
    try:
        downstream_queue.append(msg)
    finally:
        mutex.release()

def mqtt_poc(msg):
    global downstream_client
    downstream_client.on_poc(msg)

def lora_upstream(json_object):
    global mqtt
    if "data" in json_object:
        mqtt.pub("lora/upstream", json.dumps(json_object))
    else:
        downstream_client.enqueue_push_data(json.dumps(json_object), True)

def lora_downstream(json_object):
    global mqtt
    mqtt.pub("lora/downstream", json.dumps(json_object))

def lora_pull():
    global mutex
    global downstream_queue
    downstream_client.enqueue_pull_data()
    mutex.acquire()
    try:    
        q = downstream_queue.copy()
        downstream_queue.clear()
        for msg in q:
            lora_msg = json.loads(msg)
            helium_msg = helium_api.decrypt_radio(lora_msg["txpk"]["data"])
            mqtt.pub("lora/poc", json.dumps(
                {
                    "poc_id": helium_msg.poc_id, 
                    "lat": helium_api.MY_HOTSPOT['lat'],
                    "lng": helium_api.MY_HOTSPOT['lng'],
                    "gain": helium_api.MY_HOTSPOT["gain"],
                    "transmitter": lora_msg["transmitter"]
                }))
        return q
    finally:
        mutex.release()

def main():
    logging.basicConfig(level=logging.DEBUG)
    global mqtt
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
    
    # PROXY <-> MINER (gets data for radio from MINER and pubs to mqtt)
    downstream_client = lora_client(
        MINER_HOST, 
        MINER_PORT, 
        lora_downstream) 
    downstream_client.start()

    # LGW <-> PROXY (gets data from radio and pubs to mqtt)
    upstream_server = lora_server(
        PROXY_HOST, 
        PROXY_PORT, 
        lora_upstream, 
        lora_pull,
        lambda x, y : downstream_client.on_tx_ack(x, y))
    upstream_server.start()

    mqtt = mqtt_client(
        MQTT_CLIENT_ID, 
        MQTT_BROKER_HOST, 
        MQTT_CLIENT_UNAME, 
        MQTT_CLIENT_PASSW, 
        MQTT_BROKER_PORT, 
        MQTT_CA_CERT)

    mqtt.sub("lora/upstream", mqtt_upstream)
    mqtt.sub("lora/downstream", mqtt_downstream)
    mqtt.sub("lora/poc", mqtt_poc)

    while True:
        sleep(1)

if __name__ == "__main__":
    main()