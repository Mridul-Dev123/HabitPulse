#!/bin/bash
echo "Starting HabitPulse Server..."
source ./mywnv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0
