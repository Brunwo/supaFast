#!/bin/bash

# Launch the FastAPI application using uvicorn
# Use nohup to detach from the terminal and redirect output to a log file
# The PID of the uvicorn process will be echoed for the calling script

nohup uvicorn src.template.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# Get the PID of the last background command (uvicorn)
UVICORN_PID=$!

# Disown the process to ensure it continues running even if the parent shell exits
disown $UVICORN_PID

# Echo the PID so the calling script can capture it
echo $UVICORN_PID