# Model Context Protocol (MCP) Server Research Findings

This document summarizes the key tools and functionalities of the Local Filesystem, Local Terminal (Shell), and Chrome DevTools MCP servers, which are essential for the Data Analytics Agent's operation. These findings are structured similarly to the previous Jupyter Notebook MCP analysis, detailing how each server enables the agent to interact with its environment and the external world.

## 1. Local Filesystem MCP Server

The Local Filesystem MCP Server provides the agent with secure and structured access to the local file system, which is crucial for data ingestion, saving analysis results, and managing project assets.

| Tool Name | Primary Function | Agent User | Key Inputs |
| :--- | :--- | :--- | :--- |
| `read_text_file` | Reads the complete content of a file as text. | Data Ingestion Agent, Conversational Agent (for reading RAG-stored files) | `path`, `head` (optional), `tail` (optional) |
| `write_file` | Creates a new file or overwrites an existing one. | Data Ingestion Agent, EDA & RAG Agent (for saving data/code) | `path`, `content` |
| `edit_file` | Makes selective, line-based edits to a file. | Data Ingestion Agent (for config files) | `path`, `edits` (oldText, newText), `dryRun` (optional) |
| `list_directory` | Lists the contents of a directory. | Data Ingestion Agent (for browsing uploaded data) | `path` |
| `search_files` | Recursively searches for files matching a pattern. | Data Ingestion Agent | `path`, `pattern`, `excludePatterns` (optional) |
| `create_directory` | Creates a new directory. | All Agents (for project structure) | `path` |

**Implementation Strategy**: The **Data Ingestion Agent** will primarily use `list_directory` and `read_text_file` to handle user-uploaded data. The `write_file` tool is vital for all agents to save intermediate results and the final Jupyter Notebooks to the project folder, fulfilling the user's persistence requirement.

## 2. Local Terminal (Shell Command) MCP Server

The Local Terminal MCP Server allows the agent to execute system-level commands, which is necessary for tasks that require shell access, such as installing dependencies or running external scripts. While a specific official server was not found, the functionality is commonly implemented via servers like `egoist/shell-command-mcp` [1].

| Tool Name | Primary Function | Agent User | Key Inputs |
| :--- | :--- | :--- | :--- |
| `execute_command` | Executes a shell command and returns the output. | Data Ingestion Agent (for package installation, data decompression) | `command`, `timeout` (optional) |
| `run_script` | Executes a script file (e.g., `.sh`, `.py`) in the terminal. | Data Ingestion Agent | `path`, `args` (optional) |
| `get_process_status` | Checks the status of a running process. | Supervisor Agent (for monitoring long-running tasks) | `pid` |

**Implementation Strategy**: The **Data Ingestion Agent** will use `execute_command` for any necessary environment setup or data preparation steps that fall outside the scope of the Python libraries in the Jupyter environment (e.g., unzipping a large file).

## 3. Chrome DevTools MCP Server

The Chrome DevTools MCP Server provides high-fidelity, programmatic control over a web browser instance, which is essential for the **Web Research Agent** to perform human-like browsing, searching, and scraping [2].

| Tool Name | Primary Function | Agent User | Key Inputs |
| :--- | :--- | :--- | :--- |
| `navigate_page` | Navigates the browser to a specified URL. | Web Research Agent | `url` |
| `fill` / `fill_form` | Inputs text into fields or fills out entire forms. | Web Research Agent (for search bars, login) | `selector` / `fields` |
| `click` | Clicks on a specific element on the page. | Web Research Agent (for following links, submitting forms) | `selector` |
| `evaluate_script` | Executes JavaScript in the browser context. | Web Research Agent (for scraping dynamic content) | `script` |
| `take_screenshot` | Captures a screenshot of the current page. | Web Research Agent (for visual context) | `path` (optional) |
| `wait_for` | Pauses execution until a condition is met (e.g., element visible). | Web Research Agent (for handling dynamic loading) | `condition` |

**Implementation Strategy**: The **Web Research Agent** will use a combination of `navigate_page` (to go to Google/Reddit), `fill` (to enter search queries), and `click` (to follow results). For advanced scraping, `evaluate_script` can be used to extract data from dynamically loaded pages, fulfilling the requirement for "scraping like a human."

## References

[1] egoist/shell-command-mcp. *MCP server for executing shell commands.* [https://github.com/egoist/shell-command-mcp](https://github.com/egoist/shell-command-mcp)
[2] ChromeDevTools/chrome-devtools-mcp. *Chrome DevTools for coding agents.* [https://github.com/ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
[3] modelcontextprotocol/servers/src/filesystem. *Filesystem MCP Server.* [https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
