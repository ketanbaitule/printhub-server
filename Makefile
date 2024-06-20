setup-ubuntu:
	sudo apt update
	sudo apt install -y python3 python3-pip python3-venv python3-dev
	sudo apt install -y cups libcups2-dev
	python3 -m venv venv
	source venv/bin/activate
	pip install -r ./requirements.txt

setup-fedora:
	sudo dnf update -y
	sudo dnf install -y python3 python3-pip python3-devel
	sudo dnf install -y cups cups-devel
	python3 -m venv venv
	source venv/bin/activate
	pip install -r ./requirements.txt

run:
	source venv/bin/activate
	python3 ./printhub.py
