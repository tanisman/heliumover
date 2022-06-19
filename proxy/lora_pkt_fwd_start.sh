#!/bin/bash

ETH0_MAC=`cat /sys/class/net/eth0/address | sed 's/://g'`
MAC_PREFIX=`echo ${ETH0_MAC} | cut -c 1-6`
MAC_POST=`echo ${ETH0_MAC} | cut -c 7-`
REGION=`/usr/bin/region_uptd`
GATEWAY_ID="${MAC_PREFIX}fffe${MAC_POST}"
echo ${GATEWAY_ID}

docker pull sh1n3/heliumover-proxy
docker stop heliumover-proxy
docker rm heliumover-proxy

docker run -d -t -i \
-e GATEWAY_UID="${GATEWAY_ID}" \
-e HELIUM_PUBKEY='YOUR_HOTSPOT_ADDRESS' \
-e PROXY_HOST='127.0.0.1' \
-e PROXY_PORT=1681 \
-e MINER_HOST='127.0.0.1' \
-e MINER_PORT=1680 \
-e HELIUMOVER_API_KEY='YOUR_API_KEY' \
-e HELIUMOVER_API_UPSTREAM="http://api.heliumover.com/upstream" \
-e HELIUMOVER_API_DOWNSTREAM="http://api.heliumover.com/downstream" \
-e HELIUMOVER_API_HOTSPOT="http://api.heliumover.com/hotspot" \
--privileged -p 127.0.0.1:1681:1681/udp --network="host" \
--name heliumover-proxy sh1n3/heliumover-proxy:latest

cd /usr/bin && ./sx1302_test_loragw_reg
if [ "$?" != "0" ]; then
    # Run SX1308 lora pkt fwd
    if [ "${REGION}" = "EU868" ]; then
        sed -e "s|/\*.*\*/||" -e "s/AABBCCFFFEDDEEFF/${GATEWAY_ID}/g" /etc/global_conf.json.sx1257.EU868.template \ 
        | jq '.gateway_conf.serv_port_up = 1681 | .gateway_conf.serv_port_down = 1681' > /etc/global_conf.json

        /usr/bin/reset_lgw.sh start
        cd /usr/bin/ && ./sx1308_lora_pkt_fwd
    else
        echo "SX1308 region error value: ${REGION}"
    fi
else
    if [ "${REGION}" = "EU868" ]; then
        # Run SX1302 lora pkt fwd
        sed -e "s|/\*.*\*/||" -e "s/AABBCCFFFEDDEEFF/${GATEWAY_ID}/g" /etc/global_conf.json.sx1250.EU868.template \
        | jq '.gateway_conf.serv_port_up = 1681 | .gateway_conf.serv_port_down = 1681' > /etc/global_conf.json
        cd /usr/bin/ && ./sx1302_lora_pkt_fwd -c /etc/global_conf.json
    else
        echo "SX1302 region error value: ${REGION}"
    fi
fi