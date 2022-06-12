from decouple import config
GATEWAY_UID = config("GATEWAY_UID")
HELIUM_PUBKEY = config("HELIUM_PUBKEY")

PROXY_HOST = config("PROXY_HOST")
PROXY_PORT = config("PROXY_PORT", cast=int)

MINER_HOST = config("MINER_HOST")
MINER_PORT = config("MINER_PORT", cast=int)

MQTT_BROKER_HOST = config("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = config("MQTT_BROKER_PORT", cast=int, default=8883)
MQTT_CLIENT_ID = config("MQTT_CLIENT_ID")
MQTT_CA_CERT = config("MQTT_CA_CERT")
MQTT_CLIENT_UNAME = config("MQTT_CLIENT_UNAME")
MQTT_CLIENT_PASSW = config("MQTT_CLIENT_PASSW")

NO_MULTI_BROADCASTS = config("NO_MULTI_BROADCASTS", cast=bool, default=False)