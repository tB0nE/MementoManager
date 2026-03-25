#!/bin/bash

# Ensure we are in the project root
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Error: .venv not found. Please run the setup first."
    exit 1
fi

# Function to run tests
run_fast_tests() {
    echo "Running fast tests (Storage & Mocked API)..."
    PYTHONPATH=. .venv/bin/pytest tests/test_storage.py tests/test_api_mocked.py tests/test_namespaces.py tests/test_forget_update.py
}

run_live_tests() {
    echo "Running live LLM tests (Requires GPU)..."
    PYTHONPATH=. .venv/bin/pytest tests/test_live_llm.py
}

run_all_tests() {
    echo "Running all tests..."
    PYTHONPATH=. .venv/bin/pytest tests/
}

# Parse arguments
case "$1" in
    fast)
        run_fast_tests
        ;;
    live)
        run_live_tests
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo "Usage: $0 {fast|live|all}"
        echo "  fast: Run storage and mocked API tests (no GPU required)"
        echo "  live: Run end-to-end tests using the actual LLM (requires GPU)"
        echo "  all:  Run every test in the suite"
        exit 1
esac
