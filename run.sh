#!/bin/bash
# Production deployment script for Sudoku Web App

echo "🎮 Starting Sudoku Web Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Stop any existing instances
echo "Stopping existing instances..."
pkill -f "gunicorn" 2>/dev/null || true

# Start the application with gunicorn
echo "Starting production server with gunicorn..."
echo "🌐 Application will be available at: http://0.0.0.0:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
