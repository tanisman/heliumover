import paho.mqtt.client as mqtt
import threading
import logging

class mqtt_client():
    def __init__(self, client_id, host, uname, pwd, port = 8883, cafile = None) -> None:
        self.client = mqtt.Client(client_id)
        if cafile != None:
            self.client.tls_set(cafile)
        
        self.client.username_pw_set(uname, pwd)
        self.client.connect(host, port)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        self.handlers = dict()

        self.thread = threading.Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        self.thread.raise_exception()
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("[mqtt] connected")
            # resubscribe to topics
            for key in self.handlers:
                self.client.subscribe(key)
        else:
            logging.error(f"[mqtt] cannot connect mqtt broker rc={rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logging.error(f"[mqtt] disconnected rc={rc}")

    def on_message(self, client, userdata, message):
        if message.topic in self.handlers:
            self.handlers[message.topic](message.payload)
        logging.debug(f"[mqtt] topic={message.topic}, msg={message.payload}")

    def pub(self, topic, payload):
        self.client.publish(topic, payload)

    def sub(self, topic, callback):
        self.client.subscribe(topic)
        self.handlers[topic] = callback

    def worker(self):
        self.client.loop_forever()