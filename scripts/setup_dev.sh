#!/bin/bash

echo "Setting up local development environment..."

if ! docker info > /dev/null 2>&1; then
    echo "Docker is not accessible. Make sure it is running."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "No permission to access Docker socket."
    echo "Run: sudo usermod -aG docker $USER"
    echo "Then logout and login again."
    exit 1
fi

echo "Docker access confirmed"

for CANDIDATE in python3 python; do
    if command -v $CANDIDATE &> /dev/null; then
        PY_PATH=$(which $CANDIDATE)
        if [[ "$PY_PATH" != *WindowsApps* ]]; then
            PYTHON=$CANDIDATE
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3 not found or Windows Store alias detected."
    echo "Install Python from python.org and disable App Execution Aliases."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv venv || { echo "Failed to create venv"; exit 1; }
fi

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Could not find venv activation script"
    exit 1
fi

pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To start development:"
echo "  ./run_local_dev.sh"
