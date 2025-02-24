#!/bin/bash

if [ ! -d "./venv" ]
 python -m venv venv
fi

if [ ! -f "./requirements.txt" ]; then
	./venv/bin/python -m pip install --upgrade pip && ./venv/bin/pip install -r requirements.txt
fi

if [ ! -x "./run.sh" ]
	chmod +x run.sh
fi
