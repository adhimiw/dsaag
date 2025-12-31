# Phase 1 Implementation Plan: Foundation & MCP Integration

## Overview
This plan implements Phase 1 of the Data Analytics Agent, establishing the core environment, MCP server integration, and initial agent definitions. **Mistral AI is prioritized as the primary LLM provider** due to its native MCP integration and dedicated Agents API, which significantly simplifies tool integration. Google Gemini is included as a secondary option, particularly valuable for visual analysis tasks (EDA chart interpretation).

## Project Structure

```
agi/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── supervisor_agent.py    # Supervisor Agent (orchestration)
│   ├── data_ingestion_agent.py
│   └── web_research_agent.py
├── mcp_clients/
│   ├── __init__.py
│   ├── base_mcp_client.py     # Base MCP client wrapper
│   ├── jupyter_client.py      # Jupyter MCP client
│   ├── browser_client.py      # Browser/Chrome DevTools MCP client
│   ├── filesystem_client.py   # Filesystem MCP client
│   └── terminal_client.py     # Terminal/Shell MCP client
├── llm/
│   ├── __init__.py
│   ├── base_llm.py            # Base LLM interface
│   ├── google_llm.py           # Google Gemini integration
│   └── mistral_llm.py          # Mistral AI integration
├── config/
│   ├── __init__.py
│   ├── settings.py             # Configuration management
│   └── .env.example            # Environment variables template
├── utils/
│   ├── __init__.py
│   └── logger.py               # Logging utilities
├── data/                       # Data storage directory
│   └── uploads/                # User uploaded data
├── notebooks/                  # Generated Jupyter notebooks
├── outputs/                    # Analysis outputs (images, reports)
├── requirements.txt
├── pyproject.toml              # uv project configuration
├── .env                        # Environment variables (gitignored)
├── .gitignore
└── main.py                     # Entry point
```

## Implementation Steps

### Step 1: Environment Setup

1. **Create Python 3.12 virtual environment using uv:**
   - Initialize uv project: `uv init`
   - Create venv: `uv venv --python 3.12`
   - Activate venv: `.venv\Scripts\activate` (Windows)

2. **Create `requirements.txt` with dependencies:**
   - `crewai>=0.28.0` - Multi-agent framework
   - `mistralai>=1.0.0` - Mistral AI SDK (Primary LLM - native MCP support)
   - `google-generativeai>=0.3.0` - Google Gemini API (Secondary - visual analysis)
   - `mcp>=0.9.0` - Model Context Protocol client
   - `python-dotenv>=1.0.0` - Environment variable management
   - `pydantic>=2.0.0` - Data validation
   - `pydantic-settings>=2.0.0` - Settings management
   - `loguru>=0.7.0` - Logging

3. **Create `pyproject.toml` for uv:**
   - Define project metadata
   - Specify Python 3.12 requirement
   - Include build system configuration

### Step 2: Configuration Management

**File: `config/settings.py`**
- Load environment variables from `.env`
- Define settings classes using Pydantic Settings
- Configure API keys for Google Gemini and Mistral AI
- Configure MCP server endpoints (stdin/stdout or HTTP)
- Define project paths (data, notebooks, outputs)

**File: `config/.env.example`**
- Template with required environment variables:
  - `MISTRAL_API_KEY` (Required - primary LLM)
  - `GOOGLE_API_KEY` (Optional - for visual analysis tasks)
  - `PRIMARY_LLM_PROVIDER` (default: "mistral")
  - `JUPYTER_MCP_SERVER_PATH` (optional - MCP server executable path)
  - `BROWSER_MCP_SERVER_PATH` (optional - Chrome DevTools MCP server)
  - `FILESYSTEM_MCP_SERVER_PATH` (optional - Filesystem MCP server)
  - `TERMINAL_MCP_SERVER_PATH` (optional - Terminal MCP server)
  - `MCP_SERVER_TRANSPORT` (default: "stdio" or "http")

### Step 3: LLM Provider Integration

**File: `llm/base_llm.py`**
- Abstract base class for LLM providers
- Define interface: `generate()`, `stream()`, `embed()`, `create_agent()`
- Handle common error cases
- Support for tool/MCP integration

**File: `llm/mistral_llm.py`** (Primary LLM Provider)
- Implement Mistral AI integration using **Mistral Agents API**
- Use `mistralai` SDK with Agents API support
- **Native MCP Integration**: Leverage Mistral's built-in MCP support to expose MCP servers directly
- Support for Mistral Large and Mistral Medium models
- **Built-in Tools**: Utilize Mistral's Code Interpreter and Websearch connector tools
- **Agentic Workflow**: Use Mistral's planning capabilities for multi-step tasks
- Implement retry logic and error handling
- Expose MCP servers as native tools (simplifies architecture)

**File: `llm/google_llm.py`** (Secondary LLM - Visual Analysis)
- Implement Google Gemini integration
- Use `google-generativeai` SDK
- Support for Gemini Pro and Gemini Pro Vision models
- **Code Execution Tool**: Leverage Gemini's dedicated code execution for complex analysis
- **Visual Thinking**: Use Gemini 3 Flash for analyzing EDA charts and visualizations
- Implement retry logic and error handling
- Function calling wrapper for MCP tools (since Gemini doesn't have native MCP)

**File: `llm/__init__.py`**
- Export LLM factory function
- Default to Mistral as primary provider
- Allow selection between providers based on task type:
  - Mistral for general agent tasks (native MCP advantage)
  - Gemini for visual analysis tasks (Visual Thinking capability)

### Step 4: MCP Client Wrappers

**File: `mcp_clients/base_mcp_client.py`**
- Base class for MCP clients
- Handle MCP protocol communication (stdin/stdout or HTTP)
- Implement tool discovery and invocation
- Error handling and retry logic
- **Mistral Integration**: Expose MCP tools in format compatible with Mistral's native MCP support
- **Gemini Integration**: Wrap MCP tools as function calling tools for Gemini

**File: `mcp_clients/jupyter_client.py`**
- Wrap Jupyter MCP Server
- **Note**: Mistral's Code Interpreter can complement Jupyter MCP for code execution
- Implement methods:
  - `use_notebook(notebook_name, notebook_path, mode)`
  - `insert_execute_code_cell(cell_index, cell_source, timeout)`
  - `execute_cell(cell_index, timeout, stream)`
  - `read_notebook(notebook_name, response_format)`
  - `list_files(path, max_depth, pattern)`
- Expose as MCP tool for native Mistral integration

**File: `mcp_clients/browser_client.py`**
- Wrap Chrome DevTools MCP Server
- **Note**: Mistral's built-in Websearch connector can handle simple searches, but Chrome DevTools MCP provides more control for complex scraping
- Implement methods:
  - `navigate_page(url)`
  - `fill(selector, text)` / `fill_form(fields)`
  - `click(selector)`
  - `evaluate_script(script)`
  - `take_screenshot(path)`
  - `wait_for(condition)`
- Expose as MCP tool for native Mistral integration
- Consider using Mistral's Websearch for simple queries, Chrome DevTools for complex scraping

**File: `mcp_clients/filesystem_client.py`**
- Wrap Filesystem MCP Server
- Implement methods:
  - `read_text_file(path, head, tail)`
  - `write_file(path, content)`
  - `edit_file(path, edits, dry_run)`
  - `list_directory(path)`
  - `search_files(path, pattern, exclude_patterns)`
  - `create_directory(path)`

**File: `mcp_clients/terminal_client.py`**
- Wrap Terminal/Shell MCP Server
- Implement methods:
  - `execute_command(command, timeout)`
  - `run_script(path, args)`
  - `get_process_status(pid)`

### Step 5: Base Agent Class

**File: `agents/base_agent.py`**
- Abstract base class for all agents
- Integrate with CrewAI Agent class
- **Mistral Integration**: Use Mistral Agents API for agents that benefit from native MCP
- **LLM Selection Logic**: 
  - Default to Mistral for most agents (native MCP advantage)
  - Use Gemini for visual analysis tasks (EDA chart interpretation)
- Provide LLM provider access (with smart selection)
- Provide MCP client access
- **MCP Tool Exposure**: Automatically expose MCP tools to Mistral agents via native MCP support
- Define common agent methods and utilities

### Step 6: Supervisor Agent

**File: `agents/supervisor_agent.py`**
- Extend base agent
- **Use Mistral Agents API**: Leverage Mistral's planning and tool use capabilities
- Define role: "Supervisor and Orchestrator"
- Define goal: "Coordinate workflow and delegate tasks"
- Define backstory: "Expert at breaking down complex data analytics tasks"
- **Mistral Planning**: Utilize Mistral's multi-step planning for task sequencing
- Implement task routing logic:
  - Route to Data Ingestion Agent
  - Route to EDA & RAG Agent (Phase 2)
  - Route to Analysis Decision Agent (Phase 3)
  - Route to Conversational Agent (Phase 3)
- **Agent Handoffs**: Use Mistral's agent handoff capabilities for seamless delegation

### Step 7: Data Ingestion Agent

**File: `agents/data_ingestion_agent.py`**
- Extend base agent
- Define role: "Data Ingestion Specialist"
- Define goal: "Load, validate, and clean user-provided data"
- Define backstory: "Expert at data validation and quality assessment"
- Tools:
  - Filesystem MCP client: `read_text_file`, `list_directory`, `search_files`
  - Terminal MCP client: `execute_command` (for data decompression)
- Tasks:
  - Read uploaded data file
  - Perform initial validation (file format, encoding)
  - Load data into memory (pandas DataFrame)
  - Generate data schema (column names, types, missing values)
  - Perform basic cleaning (handle missing values, type conversion)
  - Write schema and cleaning log to RAG (Phase 2)

### Step 8: Web Research Agent

**File: `agents/web_research_agent.py`**
- Extend base agent
- Define role: "Web Research Specialist"
- Define goal: "Perform external searches and scrape relevant information"
- Define backstory: "Expert at web research and information gathering"
- **Hybrid Tool Strategy**:
  - **Mistral Websearch**: Use Mistral's built-in Websearch connector for simple queries
  - **Browser MCP client**: Use Chrome DevTools MCP for complex scraping (Reddit, dynamic content)
- Tools:
  - Mistral Websearch connector (native, for simple searches)
  - Browser MCP client: `navigate_page`, `fill`, `click`, `evaluate_script`, `wait_for` (for complex scraping)
- Tasks:
  - Use Mistral Websearch for straightforward Google searches
  - Use Browser MCP for navigating to specific sites (e.g., Reddit)
  - Scrape content from pages using Chrome DevTools
  - Write findings to RAG (Phase 2)

### Step 9: Main Entry Point

**File: `main.py`**
- Initialize configuration
- **Initialize Mistral as primary LLM** (with native MCP support)
- Initialize Gemini as secondary LLM (for visual tasks)
- Initialize MCP clients
- **Expose MCP servers to Mistral** via native MCP integration
- Create Supervisor Agent (using Mistral Agents API)
- Create Data Ingestion Agent
- Create Web Research Agent
- Create CrewAI Crew with Supervisor
- Implement basic CLI interface for testing
- **LLM Selection**: Automatically route visual analysis tasks to Gemini

### Step 10: Utilities and Logging

**File: `utils/logger.py`**
- Configure loguru logger
- Set log levels and formats
- Create log file handlers

**File: `.gitignore`**
- Ignore `.env` file
- Ignore `.venv/` directory
- Ignore `__pycache__/`
- Ignore `data/`, `notebooks/`, `outputs/` (or track structure only)

## Testing Strategy

1. **Unit Tests:**
   - Test MCP client wrappers (mock MCP server responses)
   - Test LLM provider integrations (mock API responses)
   - Test configuration loading

2. **Integration Tests:**
   - Test Data Ingestion Agent with sample CSV file
   - Test Web Research Agent with simple Google search
   - Test Supervisor Agent task routing

3. **Manual Testing:**
   - Verify MCP server connections
   - Test with actual Google Gemini and Mistral API calls
   - Validate agent creation and CrewAI orchestration

## Deliverables

1. ✅ Functional project structure with modular folders
2. ✅ Python 3.12 virtual environment using uv
3. ✅ Configuration management system
4. ✅ Mistral AI LLM integration (Primary - with native MCP support and Agents API)
5. ✅ Google Gemini LLM integration (Secondary - for visual analysis)
6. ✅ MCP client wrappers for Jupyter, Browser, Filesystem, and Terminal servers
7. ✅ Native MCP integration with Mistral (simplified tool exposure)
8. ✅ Base agent class and Supervisor Agent (using Mistral Agents API)
9. ✅ Data Ingestion Agent with Filesystem/Terminal MCP tools
10. ✅ Web Research Agent with hybrid approach (Mistral Websearch + Browser MCP)
11. ✅ Main entry point with basic CLI interface and smart LLM routing
12. ✅ Logging and utility functions

## Key Architectural Decisions (Based on Research)

### 1. Mistral as Primary LLM
**Rationale**: Based on comparative research findings, Mistral offers significant advantages:
- **Native MCP Integration**: Explicit support for Model Context Protocol eliminates need for complex function-calling wrappers around MCP servers
- **Dedicated Agents API**: Built-in planning, tool use, and agent handoffs align perfectly with CrewAI orchestration model
- **Built-in Tools**: Code Interpreter and Websearch connector reduce implementation complexity
- **Cost Efficiency**: Known for strong performance in reasoning tasks with better cost-efficiency

**Implementation Impact**:
- MCP servers (Jupyter, Browser, Filesystem, Terminal) can be exposed directly to Mistral
- No need to wrap MCP tools as function calls for Mistral agents
- Leverage Mistral's native tool selection and invocation

### 2. Gemini as Secondary LLM
**Rationale**: Gemini excels in specific areas:
- **Visual Thinking**: Gemini 3 Flash has strong capability for analyzing images and visual data
- **Code Execution Tool**: Dedicated code execution with iterative refinement
- **Use Case**: Primarily for EDA chart analysis and visual data interpretation

**Implementation Impact**:
- Route visual analysis tasks to Gemini automatically
- Use Gemini's Visual Thinking to analyze generated EDA charts
- Extract natural language insights from visualizations for RAG storage

### 3. MCP Integration Strategy
**Hybrid Approach**:
- **Mistral**: Native MCP support - expose servers directly
- **Gemini**: Function calling wrapper for MCP tools (when needed)
- **Preference**: Use Mistral's built-in tools (Websearch, Code Interpreter) when they suffice
- **Fallback**: Use MCP servers for advanced functionality (complex scraping, Jupyter notebooks)

### 4. Agent Workflow Optimization
- **Supervisor Agent**: Uses Mistral's planning capabilities for task sequencing
- **Tool Selection**: Agents leverage Mistral's native tool selection (no manual routing needed)
- **Agent Handoffs**: Seamless delegation using Mistral's agent capabilities
- **Code Execution**: Prefer Mistral's Code Interpreter for simple tasks, Jupyter MCP for complex analysis

## Next Steps (Phase 2)

After Phase 1 completion:
- Implement RAG system (ChromaDB + embeddings)
- Develop EDA & RAG Agent (use Gemini for chart analysis)
- Integrate RAG writing mechanism
- Test full EDA pipeline
- Leverage Mistral's Code Interpreter alongside Jupyter MCP

