#!/bin/bash
echo "Starting HabitPulse Server..."
source ./venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0
