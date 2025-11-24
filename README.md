# Airline Multi-Agent Orchestration System

A complete Python-based multi-agent system demonstrating AutoGen + MCP (Model Context Protocol) patterns for real-time aircraft telemetry anomaly detection, diagnosis, and resolution.

## 🎯 Overview

This system simulates a predictive maintenance pipeline for aircraft operations, using multiple AI agents that collaborate to:
- Monitor real-time telemetry data
- Detect anomalies using threshold-based and ML-based methods
- Diagnose root causes using LLM reasoning
- Generate maintenance recommendations

## ✈️ Business Value

### Airline Benefits

**Reduced AOG (Aircraft On Ground) Events**
- Early anomaly detection prevents catastrophic failures
- Predictive maintenance reduces unscheduled downtime
- Faster diagnosis minimizes maintenance windows

**Predictive Maintenance**
- ML-based anomaly detection identifies issues before they become critical
- Pattern recognition across telemetry parameters
- Reduced false alarms through multi-stage validation

**Faster Diagnosis**
- LLM-powered root cause analysis in seconds
- Automated subsystem identification
- Severity assessment for prioritization

**Improved Flight Safety**
- Continuous monitoring of critical parameters
- Real-time anomaly detection and escalation
- Proactive maintenance recommendations

**Reduced Operational Costs**
- Minimize emergency maintenance expenses
- Optimize maintenance scheduling
- Reduce parts inventory through better planning
- Lower fuel costs from early issue detection

## 🧠 AutoGen + MCP Demonstration Value

**Agent Collaboration**
- Multiple specialized agents working together
- Clear separation of concerns (monitoring, validation, diagnosis, resolution)
- Autonomous agent-to-agent communication

**Tool-Calling Workflows**
- ML model integrated as a tool for anomaly validation
- LLM agents using OpenAI API for reasoning
- MCP-style shared memory for agent coordination

**Interpretable Decisions**
- Clear CLI output showing each agent's reasoning
- Traceable pipeline from telemetry to resolution
- Transparent ML model scores and thresholds

**Autonomous Reasoning Pipeline**
- Self-orchestrating agent workflow
- Conditional routing based on anomaly detection
- No human intervention required for normal operations

**Real-World Use Case**
- Practical application in aviation maintenance
- Scalable to other IoT/telemetry monitoring scenarios
- Demonstrates production-ready patterns

## 🏗️ Architecture

```
Telemetry Simulator
    ↓
TelemetryAgent (Threshold Detection)
    ↓
AnomalyAgent (ML Validation)
    ↓
DiagnosisAgent (LLM Root Cause Analysis)
    ↓
ResolutionAgent (LLM Maintenance Recommendations)
    ↑
OrchestratorAgent (Shared Memory & Routing)
```

### Components

1. **TelemetrySimulator**: Generates continuous aircraft telemetry (RPM, Pressure, Vibration, EGT) with anomaly injection
2. **TelemetryAgent**: Threshold-based anomaly detection
3. **AnomalyAgent**: ML-based anomaly confirmation using Isolation Forest
4. **DiagnosisAgent**: LLM-powered root cause analysis
5. **ResolutionAgent**: LLM-generated maintenance action plans
6. **OrchestratorAgent**: Pipeline coordination and shared memory management

## 📋 Prerequisites

- Python 3.9 or higher (tested on Python 3.12.3)
- OpenAI API key
- Internet connection (for OpenAI API calls)
- Ubuntu/Linux or Windows (platform-independent)

## 🚀 Installation

### Step 1: Clone or Navigate to Project

```bash
cd AutoGen_POC
```

### Step 2: Set Up Virtual Environment

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

Or use the provided setup scripts:

**Windows:**
```powershell
.\setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key

Create a `config.json` file from the example:

**Windows:**
```powershell
copy config.json.example config.json
```

**Linux/macOS:**
```bash
cp config.json.example config.json
```

Then edit `config.json` and replace `"your-openai-api-key-here"` with your actual OpenAI API key:

```json
{
    "openai_api_key": "sk-your-actual-api-key-here",
    ...
}
```

**Note:** The `config.json` file is in `.gitignore` to protect your API key from being committed to version control.

## 🎮 Usage

### Run the Orchestrator

From the project root:

```bash
python run.py
```

Or directly:

```bash
python -m airline_orchestrator.main
```

### Expected Output

The system will:
1. Initialize the ML model (train on synthetic baseline data)
2. Initialize all agents
3. Process 8 cycles of telemetry data
4. Display telemetry readings with Rich formatting
5. Show agent analysis at each stage
6. Print pipeline summaries and final statistics

Example output:
```
--- New Telemetry ---
RPM=9200 | Pressure=1820 | Vibration=0.92 | EGT=740

[TelemetryAgent] High vibration detected
[AnomalyAgent] ML confirms anomaly (score=0.91) → Escalating
[DiagnosisAgent] Root cause: Fan blade fatigue
[ResolutionAgent] Recommendation: Inspect fan assembly within next 3 hours
```

## 📁 Project Structure

```
AutoGen_POC/
├── airline_orchestrator/
│   ├── __init__.py
│   ├── telemetry_simulator.py    # Telemetry generation with anomalies
│   ├── ml_model.py                # Isolation Forest anomaly detector
│   ├── agents.py                  # All AutoGen agents
│   ├── orchestrator.py            # Pipeline orchestration
│   └── main.py                    # Entry point
├── venv/                          # Virtual environment (created)
├── requirements.txt               # Python dependencies
├── setup.bat                      # Windows setup script
├── setup.sh                       # Linux/macOS setup script
├── run.py                         # Convenience runner
└── README.md                      # This file
```

## 🔧 Configuration

All configuration is managed through `config.json`. Edit this file to customize:

### Adjust Number of Cycles

Edit `config.json`:

```json
{
    "orchestrator": {
        "num_cycles": 10,
        "anomaly_probability": 0.15
    }
}
```

### Adjust Anomaly Probability

Edit `config.json`:

```json
{
    "orchestrator": {
        "num_cycles": 8,
        "anomaly_probability": 0.20
    }
}
```

### Change OpenAI Models

Edit `config.json`:

```json
{
    "models": {
        "diagnosis": "gpt-4o",
        "resolution": "gpt-4o",
        "monitoring": "gpt-4o-mini"
    }
}
```

### Adjust ML Model Training

Edit `config.json`:

```json
{
    "ml_model": {
        "n_samples": 2000,
        "contamination": 0.15
    }
}
```

## 🧪 Technical Details

### ML Model
- **Algorithm**: Isolation Forest (scikit-learn)
- **Training**: Synthetic baseline data (1000 samples)
- **Features**: RPM, Pressure, Vibration, EGT
- **Storage**: In-memory only (no file I/O)

### LLM Agents
- **Models**: GPT-4-turbo (diagnosis/resolution), GPT-4o-mini (monitoring/validation)
- **Temperature**: 0.3 (for consistent outputs)
- **Format**: JSON responses for structured data

### MCP Pattern
- **Shared Memory**: Python dictionary accessible to all agents
- **Tool Calling**: ML model exposed as callable tool
- **Autonomous Routing**: Orchestrator routes based on agent outputs

## 🐛 Troubleshooting

### "Config file not found" or "OpenAI API key not configured"
- Ensure `config.json` exists in the project root
- Copy from `config.json.example` if missing: `cp config.json.example config.json`
- Edit `config.json` and set your `openai_api_key` value
- Make sure the JSON syntax is valid (no trailing commas, proper quotes)

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version` (should be 3.8+)

### API Rate Limits
- OpenAI API has rate limits based on your plan
- If you hit limits, add delays between cycles in `orchestrator.py`

### ML Model Training Warnings
- Warnings about convergence are normal for Isolation Forest
- Model will still function correctly

## 📊 Performance Considerations

- **API Calls**: Each cycle with an anomaly makes 2 LLM API calls (diagnosis + resolution)
- **Latency**: ~2-5 seconds per cycle with anomalies (due to LLM calls)
- **Cost**: Uses GPT-4-turbo for diagnosis/resolution (higher cost) and GPT-4o-mini for monitoring (lower cost)

## 🔒 Security Notes

- **Never commit your `config.json` file to version control** - it's already in `.gitignore`
- The `config.json.example` file is safe to commit (contains placeholder values)
- Keep your API key secure and never share it publicly
- If you need to share the project, ensure `config.json` is excluded

## 📝 License

This is a demonstration project. Use at your own discretion.

## 🤝 Contributing

This is a POC project. For production use, consider:
- Adding unit tests
- Implementing proper error handling
- Adding logging instead of console prints
- Implementing retry logic for API calls
- Adding configuration files
- Implementing database storage for history

## 📚 References

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

---

**Built with**: Python, AutoGen, OpenAI, scikit-learn, Rich

**Demonstrates**: Multi-agent systems, MCP patterns, ML+LLM integration, CLI applications

