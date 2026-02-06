#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to the project root
export PYTHONPATH="$SCRIPT_DIR"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run Streamlit
# nohup execution should be handled by the user invocation if needs backgrounding, 
# but for simplicity we run foreground here and let user choose.
echo "Starting Streamlit from Root: $SCRIPT_DIR"
echo "PYTHONPATH: $PYTHONPATH"

# Run streamlit pointing to the file
streamlit run src/dashboard/app.py --server.port 8501
