#!/bin/bash

# Port to run the API on
PORT=7087

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: .venv directory not found. Please ensure the virtual environment is set up."
    exit 1
fi

# Check if model exists
MODEL_PATH=$(grep MODEL_PATH .env | cut -d '=' -f2)
if [ ! -f "$MODEL_PATH" ]; then
    echo "Warning: Model not found at $MODEL_PATH."
    echo "Please check your .env file or ensure the model is in the models/ folder."
fi

echo "Starting Local LLM Memory API on port $PORT..."
echo "Using model: $MODEL_PATH"

# Run the API
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT
