#!/bin/bash

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete! To activate the environment, run:"
echo "source venv/bin/activate"
echo ""
echo "Next steps:"
echo "1. Copy config.json.example to config.json:"
echo "   cp config.json.example config.json"
echo ""
echo "2. Edit config.json and add your OpenAI API key"
echo ""
echo "3. Run the system:"
echo "   python run.py"
echo ""

