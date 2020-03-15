NAME := tagpi
# for a server installation, these packages are also required: libatlas-base-dev libopenjp2-7-dev
.PHONY: install
install:
	sudo apt-get install python3 python3-pip mosquitto
	sudo pip install -r requirements.txt
	sudo cp remotes/lircrc /etc/lirc/
	sudo cp remotes/lircd.conf /etc/lirc/lircd.conf.d/
	sudo systemctl lircd.service restart