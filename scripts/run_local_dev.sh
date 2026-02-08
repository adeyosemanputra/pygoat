#!/bin/bash

echo "🚀 PyGoat Local Development Mode"
echo "================================"
echo ""
echo "✅ This will start PyGoat on port 8001 for development"
echo "✅ Keep docker-compose running for nginx and labs"
echo ""
echo "📌 Main App: http://localhost:8001"
echo "📌 Labs (via nginx): http://localhost:8000/labs/*"
echo ""
echo "Starting server..."

# Detect a real Python (ignore Windows Store aliases)
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
    echo "❌ Python 3 not found or Windows Store alias detected."
    echo "💡 Install Python from python.org and disable App Execution Aliases."
    exit 1
fi

# Activate venv if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo "❌ venv not found. Run ./scripts/setup_dev.sh first."
        exit 1
    fi
fi

# Ensure migrations are up to date
$PYTHON manage.py migrate --noinput || exit 1

# Start development server on port 8001 (127.0.0.1 for Windows compatibility)
$PYTHON manage.py runserver 127.0.0.1:8001
