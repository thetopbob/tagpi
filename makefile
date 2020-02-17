NAME := tagpi

.PHONY: install
install:
	sudo apt-get install python3 python3-pip libatlas-base-dev libopenjp2-7-dev mosquitto
	sudo pip install -r requirements.txt
