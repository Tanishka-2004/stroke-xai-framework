@echo off
title NeuroPulse XAI - Stroke Framework Server (RA2311003011560)
echo ======================================================================
echo Starting NeuroPulse XAI: Stroke Risk, Severity, and Outcome Framework
echo Registration Number: RA2311003011560
echo ======================================================================
cd /d "%~dp0"
echo Launching Uvicorn Server at http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
