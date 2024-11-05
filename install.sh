#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install build tools
pip install --upgrade pip build wheel

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"

# Ensure template directory exists
mkdir -p src/template

# Copy environment template if it doesn't exist
if [ ! -f src/template/.env ]; then
    cp src/template/.env.template src/template/.env
    echo "Created .env file from template. Please update with your settings."
fi

# Create a .env file in the root if it doesn't exist
if [ ! -f .env ]; then
    cp src/template/.env.template .env
    echo "Created root .env file from template. Please update with your settings."
fi
