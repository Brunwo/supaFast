# #!/bin/bash

# # Create and activate virtual environment
# python -m venv venv
# source venv/bin/activate

# # Install build tools
# pip install --upgrade pip build wheel

# # Install the package in editable mode with dev dependencies
# pip install -e ".[dev]"

# # Create a .env file in the root if it doesn't exist
# if [ ! -f .env ]; then
#     cp src/template/.env.template .env
#     echo "Created root .env file from template. Please update with your settings."
# fi


pip uninstall fastapi-supabase -y

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]" --no-cache-dir