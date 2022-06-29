#!/bin/sh

# disable default pktfwd
DEFAULT_PKTFWD=`balena container ls --format '{{.Names}}' | grep "pktfwd_"`
if [ "${DEFAULT_PKTFWD}" != "" ]; then
    echo "Stopping default pktfwd container: ${DEFAULT_PKTFWD}"
    balena container stop ${DEFAULT_PKTFWD}
    balena container rm ${DEFAULT_PKTFWD}
fi

# get custom heliumover pktfwd
balena pull docker.io/sh1n3/heliumovoer-sensecap-pktfwd
balena stop heliumover-sensecap-pktfwd
balena rm heliumover-sensecap-pktfwd

# run custom pktfwd
balena run -d -t -i \
-e REGION="EU868" \
--privileged --network="host" \
--name heliumover-sensecap-pktfwd sh1n3/heliumovoer-sensecap-pktfwd:latest

# run proxy
balena pull sh1n3/heliumover-proxy
balena stop heliumover-proxy
balena rm heliumover-proxy

balena run -d -t -i \
-e GATEWAY_UID="AA555A0000000000" \
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