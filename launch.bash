#!/bin/bash

pyenv local 3.10.12
cd app/ && pip install -r requirements.txt
python main.py