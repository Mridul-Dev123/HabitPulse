@echo off
echo Starting HabitPulse Server...
call .\mywnv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0
