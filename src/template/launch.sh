#!/bin/bash

# Activate virtual environment
source ../venv/bin/activate

# Run the FastAPI application using uvicorn
uvicorn main:app --reload --port 8000 