# Data Analytics Agent

A sophisticated multi-agent data analytics platform that automates the entire data science workflow, from data ingestion and exploratory analysis (EDA) to predictive modeling and intelligent, context-aware conversational querying.

## Architecture

The system employs a multi-agent architecture built on:
- **CrewAI Framework**: For multi-agent orchestration
- **Model Context Protocol (MCP)**: For tool integration (Jupyter, Browser, Filesystem, Terminal)
- **Retrieval-Augmented Generation (RAG)**: For memory and context storage
- **Mistral AI**: Primary LLM with native MCP support
- **Google Gemini**: Secondary LLM for visual analysis tasks

## Project Structure

```
agi/
├── agents/              # Agent implementations
├── mcp_clients/         # MCP server client wrappers
├── llm/                 # LLM provider integrations
├── config/              # Configuration management
├── utils/               # Utility functions
├── data/                # Data storage
├── notebooks/           # Generated Jupyter notebooks
└── outputs/             # Analysis outputs
```

## Setup

### Prerequisites

- Python 3.12 (or 3.11+)
- [uv](https://github.com/astral-sh/uv) package manager
- Mistral AI API key
- Google API key (optional, for visual analysis)

### Quick Start

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Create virtual environment**:
   ```bash
   uv venv --python 3.12
   # Or if 3.12 is not available:
   uv venv --python 3.11
   ```

3. **Activate virtual environment**:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - Windows CMD: `.venv\Scripts\activate.bat`
   - Linux/Mac: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   - The `.env` file should already exist (copied from `config/.env.example`)
   - Edit `.env` and add your API keys:
     ```env
     MISTRAL_API_KEY=your_actual_mistral_api_key
     GOOGLE_API_KEY=your_actual_google_api_key  # Optional
     ```
   - Get API keys:
     - Mistral AI: https://console.mistral.ai/
     - Google Gemini: https://makersuite.google.com/app/apikey

6. **Run the agent**:
   ```bash
   python main.py
   ```

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Configuration

Edit `.env` file with your settings:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
PRIMARY_LLM_PROVIDER=mistral
```

## Phase 1 Status

✅ Project structure created
✅ Configuration management
✅ LLM provider integrations (Mistral & Google)
✅ MCP client wrappers (Jupyter, Browser, Filesystem, Terminal)
✅ Base agent class
✅ Supervisor Agent
✅ Data Ingestion Agent
✅ Web Research Agent
✅ Main entry point

## Next Steps (Phase 2)

- Implement RAG system (ChromaDB + embeddings)
- Develop EDA & RAG Agent
- Integrate RAG writing mechanism
- Test full EDA pipeline

## Key Features

- **Native MCP Integration**: Leverages Mistral's native MCP support for simplified tool integration
- **Hybrid LLM Strategy**: Uses Mistral for general tasks, Gemini for visual analysis
- **Modular Architecture**: Clean separation of concerns with modular folder structure
- **Extensible Design**: Easy to add new agents, tools, and LLM providers

## License

MIT

