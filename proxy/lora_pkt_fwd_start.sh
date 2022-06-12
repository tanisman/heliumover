#!/bin/bash

ETH0_MAC=`cat /sys/class/net/eth0/address | sed 's/://g'`
MAC_PREFIX=`echo ${ETH0_MAC} | cut -c 1-6`
MAC_POST=`echo ${ETH0_MAC} | cut -c 7-`
REGION=`/usr/bin/region_uptd`
GATEWAY_ID="${MAC_PREFIX}fffe${MAC_POST}"
echo ${GATEWAY_ID}

docker stop helium-proxy
docker rm helium-proxy

docker run -d -t -i \
-e GATEWAY_UID="${GATEWAY_ID}" \
-e HELIUM_PUBKEY='112FsHPgF1G3dPUGytxZY4LpanbHU8z9PjFMgTCfqTVyK2x7bBvh' \
-e PROXY_HOST='127.0.0.1' \
-e PROXY_PORT=1681 \
-e MINER_HOST='127.0.0.1' \
-e MINER_PORT=1680 \
-e MQTT_BROKER_HOST='mukzy0.stackhero-network.com' \
-e MQTT_BROKER_PORT=8883 -e MQTT_CA_CERT='proxy/isrgrootx1.pem' \
-e MQTT_CLIENT_ID='lora-proxy-${GATEWAY_PROXY}' \
-e MQTT_CLIENT_UNAME='admin' \
-e MQTT_CLIENT_PASSW='fzzpGjZIGMQZgMTdjaFSIMr6JtEfn3UN' \
--privileged -p 127.0.0.1:1681:1681/udp --network="host" \
--name helium-proxy sh1n3/heliumproxy:1.1.5

cd /usr/bin && ./sx1302_test_loragw_reg
if [ "$?" != "0" ]; then
    # Run SX1308 lora pkt fwd
    if [ "${REGION}" = "EU868" ]; then
        sed "s/AABBCCFFFEDDEEFF/${GATEWAY_ID}/g" /etc/global_conf.json.sx1257.EU868.template > /etc/global_conf.json
        /usr/bin/reset_lgw.sh start
        cd /usr/bin/ && ./sx1308_lora_pkt_fwd
    else
        echo "SX1308 region error value: ${REGION}"
    fi
else
    if [ "${REGION}" = "EU868" ]; then
        # Run SX1302 lora pkt fwd
        sed "s/AABBCCFFFEDDEEFF/${GATEWAY_ID}/g" /etc/global_conf.json.sx1250.EU868.template > /etc/global_conf.json
        cd /usr/bin/ && ./sx1302_lora_pkt_fwd -c /etc/global_conf.json
    else
        echo "SX1302 region error value: ${REGION}"
    fi
fi