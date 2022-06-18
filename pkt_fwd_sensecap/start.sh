#!/bin/bash

FAN_PIN=13

cron start 

WAIT_GPIO() {
    sleep 0.1
}

echo "****** SX1302 Packet Forwarder ******" | tee -a /var/log/pktfwd/pktfwd.log
echo "" | tee -a /var/log/pktfwd/pktfwd.log

echo "Starting fan..."
echo "$FAN_PIN" > /sys/class/gpio/export; WAIT_GPIO
echo "out" > /sys/class/gpio/gpio$FAN_PIN/direction; WAIT_GPIO
echo "1" > /sys/class/gpio/gpio$FAN_PIN/value; WAIT_GPIO

while true; do
    date | tee -a /var/log/pktfwd/pktfwd.log
    if [[ ! "x$REGION" = "x" ]]; then
        echo "Find region [$REGION] from REGION" | tee -a /var/log/pktfwd/pktfwd.log
        break
    elif [[ ! "x$REGION_OVERRIDE" = "x" ]]; then
        REGION=$REGION_OVERRIDE
        echo "Find region [$REGION] from REGION_OVERRIDE" | tee -a /var/log/pktfwd/pktfwd.log
        break
    elif [ -f /var/data/region ]; then
        REGION=$(head -n 1 /var/data/region)
        echo "Find region [$REGION] from /var/data/region" | tee -a /var/log/pktfwd/pktfwd.log
        break
    else
        echo "Can't find region, sleep 60s and try again..." | tee -a /var/log/pktfwd/pktfwd.log
        sleep 60
    fi
done

echo "The region of this gateway is [$REGION]" | tee -a /var/log/pktfwd/pktfwd.log

if [[ "x$REGION" == "xUS915" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.US915"
elif [[ "x$REGION" == "xEU868" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.EU868"
elif [[ "x$REGION" == "xAU915" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AU915"
elif [[ "x$REGION" == "xCN470" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.CN470"
elif [[ "x$REGION" == "xIN865" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.IN865"
elif [[ "x$REGION" == "xKR920" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.KR920"
elif [[ "x$REGION" == "xRU864" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.RU864"
elif [[ "x$REGION" == "xAS923" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923"
elif [[ "x$REGION" == "xAS923_1" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_1"
elif [[ "x$REGION" == "xAS923_2" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_2"
elif [[ "x$REGION" == "xAS923_3" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_3"
elif [[ "x$REGION" == "xAS923_4" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_4"
elif [[ "x$REGION" == "xregion_us915" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.US915"
elif [[ "x$REGION" == "xregion_eu868" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.EU868"
elif [[ "x$REGION" == "xregion_au915" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AU915"
elif [[ "x$REGION" == "xregion_cn470" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.CN470"
elif [[ "x$REGION" == "xregion_in865" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.IN865"
elif [[ "x$REGION" == "xregion_kr920" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.KR920"
elif [[ "x$REGION" == "xregion_ru864" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.RU864"
elif [[ "x$REGION" == "xregion_as923_1" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_1"
elif [[ "x$REGION" == "xregion_as923_2" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_2"
elif [[ "x$REGION" == "xregion_as923_3" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_3"
elif [[ "x$REGION" == "xregion_as923_4" ]]; then
    GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.AS923_4"
else
    echo "[$REGION] doesn't match any existing region, sleep 60s and exit..."
    sleep 60
    exit 0
    # GCONF="/opt/sx1302_hal/packet_forwarder/global_conf.json.sx1250.EU868"
fi

echo "Load the following configuration files:" | tee -a /var/log/pktfwd/pktfwd.log
echo "- $GCONF" | tee -a /var/log/pktfwd/pktfwd.log
echo "" | tee -a /var/log/pktfwd/pktfwd.log

# cd /opt/sx1302_hal/packet_forwarder
./lora_pkt_fwd -c $GCONF | tee -a /var/log/pktfwd/pktfwd.log
