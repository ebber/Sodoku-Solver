#!/bin/bash
# Quick development server script for Sudoku Web App

echo "🎮 Starting Sudoku Web Application (Development Mode)..."

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
pip install -r requirements.txt -q

# Stop any existing instances
echo "Stopping existing instances..."
pkill -f "python app.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

# Start the development server
echo ""
echo "🌐 Application starting at: http://localhost:5000"
echo ""
echo "✨ Features:"
echo "   - 3 Difficulty levels (Easy/Medium/Hard)"
echo "   - Lives system (3 lives)"
echo "   - Light/Dark theme toggle"
echo "   - Hints, undo/redo, pencil marks"
echo "   - Invalid moves auto-revert"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
