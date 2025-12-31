# Setup Guide

## Prerequisites

- Python 3.12 (or 3.11+)
- pip (Python package manager)

## Step 1: Install uv

`uv` is a fast Python package manager. Install it using one of these methods:

### Option A: Using pip (Recommended)
```bash
pip install uv
```

### Option B: Using PowerShell (Windows)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Option C: Using curl (Linux/Mac)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verify Installation
```bash
uv --version
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12

# If Python 3.12 is not available, use 3.11+
uv venv --python 3.11
```

## Step 3: Activate Virtual Environment

### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)
```cmd
.venv\Scripts\activate.bat
```

### Linux/Mac
```bash
source .venv/bin/activate
```

## Step 4: Install Dependencies

### Option A: Using the installation script (Windows PowerShell)
```powershell
.\install_dependencies.ps1
```

### Option B: Manual installation
```bash
# Activate virtual environment first
.venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
.venv\Scripts\activate.bat  # Windows CMD

# Install dependencies using uv (recommended - faster)
uv pip install -r requirements.txt

# Also install the new Google GenAI package
uv pip install google-genai

# OR using regular pip
pip install -r requirements.txt
pip install google-genai
```

## Step 5: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   # The .env file should already be created, but if not:
   copy config\.env.example .env
   ```

2. **Edit `.env` file** and add your API keys:
   ```env
   MISTRAL_API_KEY=your_actual_mistral_api_key
   GOOGLE_API_KEY=your_actual_google_api_key  # Optional
   ```

   **Get API Keys:**
   - Mistral AI: https://console.mistral.ai/
   - Google Gemini: https://makersuite.google.com/app/apikey

## Step 6: Verify Installation

Run the main script to verify everything is set up correctly:

```bash
python main.py
```

You should see initialization messages without errors.

## Troubleshooting

### uv not found
- Make sure `uv` is installed: `pip install uv`
- Check if it's in your PATH: `where uv` (Windows) or `which uv` (Linux/Mac)

### Python version issues
- Check Python version: `python --version`
- If you need Python 3.12, download from https://www.python.org/downloads/

### Import errors
- Make sure virtual environment is activated
- Reinstall dependencies: `uv pip install -r requirements.txt`

### API key errors
- Verify `.env` file exists in project root
- Check that API keys are correctly set (no extra spaces or quotes)
- Ensure `.env` file is not in `.gitignore` (it should be ignored for security)

## Next Steps

After successful setup, you're ready for:
- Phase 2: RAG & EDA Core Development
- Testing agent functionality
- Integrating MCP servers

