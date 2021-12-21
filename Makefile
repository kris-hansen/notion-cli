.PHONY: setup format build

setup:
	python3 -m venv ./venv && source ./venv/bin/activate && pip install pip --upgrade && pip install -r requirements.txt && pip install -e . || rm -r venv

format:
	source ./venv/bin/activate && isort . && black .

build:
	source ./venv/bin/activate && pyinstaller -n notion --onefile cli.py
