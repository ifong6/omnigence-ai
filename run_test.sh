#!/bin/bash
# Helper script to run tests with proper Python environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to project root
export PYTHONPATH="$SCRIPT_DIR"

# Run the test using the virtual environment Python
"$SCRIPT_DIR/.venv/bin/python" "$@"
