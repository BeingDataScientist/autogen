# Quick Execution Guide

## 🚀 How to Run the System

### Step 1: Set Up Virtual Environment (First Time Only)

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Or use the automated setup script:

**Windows:**
```powershell
.\setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

### Step 3: Configure Your OpenAI API Key

Edit `config.json` and replace `"your-openai-api-key-here"` with your actual API key:

```json
{
    "openai_api_key": "sk-your-actual-api-key-here",
    ...
}
```

**Important:** The `config.json` file already exists. Just open it and update the API key value.

### Step 4: Run the System

From the project root directory:

```bash
python run.py
```

Or directly:

```bash
python -m airline_orchestrator.main
```

## 📋 Quick Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `config.json` updated with your OpenAI API key
- [ ] Run `python run.py`

## 🎯 Expected Output

You should see:
1. System initialization messages
2. ML model training progress
3. Agent initialization
4. 8 cycles of telemetry data with agent analysis
5. Pipeline summaries for each cycle
6. Final summary statistics

## ⚠️ Troubleshooting

**"Config file not found"**
- Make sure you're running from the project root directory
- Ensure `config.json` exists in the same directory as `run.py`

**"OpenAI API key not configured"**
- Open `config.json` and verify the `openai_api_key` field has your actual key
- Make sure the key starts with `sk-` and is properly quoted in JSON

**"Module not found" errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Import errors**
- Ensure you're in the project root directory
- Check that `airline_orchestrator/` folder exists with all Python files

## 🔄 Daily Usage

After initial setup, you only need to:

1. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

2. Run the system:
   ```bash
   python run.py
   ```

That's it! 🎉

