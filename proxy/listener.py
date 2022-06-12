from time import sleep
from proxy_config import *
from mqtt_client import mqtt_client
from lora_server import lora_server
from lora_client import lora_client
from threading import Lock
import logging

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

def lora_upstream(json_object):
    global mqtt
    mqtt.pub("lora/upstream", json_object)

def lora_downstream(json_object):
    global mqtt
    mqtt.pub("lora/downstream", json_object)

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
    global mqtt
    global downstream_client
    global upstream_server
    
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

    while True:
        logging.info("Sleeping...")
        sleep(1)

if __name__ == "__main__":
    main()