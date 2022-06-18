FROM debian:buster-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
	sudo \
	ca-certificates \
	findutils \
	gnupg \
	dirmngr \
	netbase \
	curl \
	udev \
	procps \
	$( \
		if apt-cache show 'iproute' 2>/dev/null | grep -q '^Version:'; then \
		echo 'iproute'; \
		else \
		echo 'iproute2'; \
		fi \
	) \
	less \
	kmod \
	nano \
	net-tools \
	ifupdown \
	iputils-ping \
	i2c-tools \
	usbutils \
	git \
	build-essential \
	wget \
	logrotate \
	cron

WORKDIR /opt
RUN git clone https://github.com/helium/sx1302_hal
WORKDIR /opt/sx1302_hal
COPY reset_lgw.sh ./
COPY reset_lgw.sh start.sh ./packet_forwarder/
COPY loragw_reg.c ./libloragw/src/
RUN make


WORKDIR /etc/logrotate.d
COPY pkt_fwd ./
RUN chmod 644 ./pkt_fwd

WORKDIR /etc/cron.d
COPY log_crontab ./
RUN crontab /etc/cron.d/log_crontab

WORKDIR /opt/sx1302_hal/packet_forwarder

COPY global_conf.json.sx1250.AS923_1 \
    global_conf.json.sx1250.AS923_2 \ 
    global_conf.json.sx1250.AS923_3 \ 
    global_conf.json.sx1250.AS923_4 \ 
    global_conf.json.sx1250.KR920 \
    global_conf.json.sx1250.EU868 \
    global_conf.json.sx1250.IN865 \
    global_conf.json.sx1250.RU864 \
    global_conf.json.sx1250.AU915 \
    global_conf.json.sx1250.US915 \
    global_conf.json.sx1250.AS923 \
    global_conf.json.sx1250.CN470 \
    ./

RUN chmod +x start.sh lora_pkt_fwd reset_lgw.sh

ENTRYPOINT [ "./start.sh" ]