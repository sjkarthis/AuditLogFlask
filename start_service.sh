#!/bin/bash

# Activate virtual environment if needed
# source venv/bin/activate

# Start the Flask application
export FLASK_APP=app/main.py
flask run --host=0.0.0.0
