@echo off
if not exist "venv\" (python -m venv venv)
if exist requirements.txt (venv\Scripts\python.exe -m pip install --upgrade pip && venv\Scripts\pip install -r requirements.txt)
venv\Scripts\python.exe main.py