@echo off
cd /d "%~dp0.."
call venv2\Scripts\activate
"%~dp0..\venv2\Scripts\python.exe" flask_app\FaceRecognition.py