#!/bin/sh
APP="lora_pkt_fwd"
CFG="global_conf.json"
CFG_HELIUMOVER="global_conf_heliumover.json"
EXE_PATH="/opt"
PIDFILE="/var/run/${APP}.pid"
rfpower="0"

do_stop() {
    target_pid=`pidof $APP`
    if [ $? = "0" ]; then
        kill -15 $target_pid
        sleep 1
        rm -f $PIDFILE
    else
        echo "$APP isn't running."
    fi
}

do_start() {
    target_pid=`pidof $APP`
    if [ $? = "0" ];then
        echo "$APP is running."
        exit 1
    fi

    gateway_id=$(jq -r '.gateway_conf'.'gateway_ID' $EXE_PATH/$CFG)
    jq '.gateway_conf.serv_port_up = 1681 | .gateway_conf.serv_port_down = 1681' $EXE_PATH/$CFG > $EXE_PATH/$CFG_HELIUMOVER
    docker pull sh1n3/heliumover-proxy
    docker stop heliumover-proxy
    docker rm heliumover-proxy
    docker run -d -t -i \
    -e GATEWAY_UID="${gateway_id}" \
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

    if [ -e $EXE_PATH/local_tx_power ]; then
        rfpower=`cat $EXE_PATH/local_tx_power`
    fi

    /usr/bin/reset_lgw.sh start
    $EXE_PATH/$APP -c $EXE_PATH/$CFG_HELIUMOVER -x $rfpower &
    sleep 1
    echo `pidof $APP` > $PIDFILE
}

case $1 in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
	restart)
        do_stop
        do_start
        ;;
    *)
        echo "$0 <start|stop|restart>"
        ;;
esac
