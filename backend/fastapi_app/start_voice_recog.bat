@echo off
cd /d "%~dp0.."
call venv\Scripts\activate
"%~dp0..\venv\Scripts\python.exe" fastapi_app\VoiceCommand.py