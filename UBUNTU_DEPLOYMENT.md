# Ubuntu Deployment Guide (Python 3.12.3)

## Quick Setup for Ubuntu

### 1. Verify Python Version

```bash
python3 --version
# Should show: Python 3.12.3
```

If you need to install Python 3.12.3:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip
```

### 2. Clone/Navigate to Project

```bash
cd AutoGen_POC
```

### 3. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API Key

```bash
# Copy example config
cp config.json.example config.json

# Edit config.json with your favorite editor
nano config.json
# or
vim config.json
# or
gedit config.json
```

Update the `openai_api_key` field in `config.json` with your actual API key.

### 5. Run the System

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the orchestrator
python run.py
```

## Daily Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run the system
python run.py
```

## Troubleshooting

### "python3.12: command not found"
- Install Python 3.12: `sudo apt install python3.12 python3.12-venv`
- Or use `python3` if it points to 3.12.3

### "Module not found" errors
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Permission denied on setup.sh
- Make executable: `chmod +x setup.sh`

### Config file not found
- Ensure you're in the project root directory
- Check that `config.json` exists: `ls -la config.json`

## System Requirements

- **OS**: Ubuntu 20.04+ (or any Linux distribution)
- **Python**: 3.12.3 (or 3.9+)
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 500MB free space
- **Network**: Internet connection for OpenAI API calls

## Notes

- The system is platform-independent and works identically on Ubuntu and Windows
- All configuration is in `config.json` (no environment variables needed)
- The virtual environment isolates dependencies from system Python

