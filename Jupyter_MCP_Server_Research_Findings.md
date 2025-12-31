# Jupyter MCP Server Research Findings

The `datalayer/jupyter-mcp-server` provides a robust set of tools for AI agents to interact with Jupyter Notebooks.

## Key Tools for Data Analytics Agent

| Tool Name | Description | Key Inputs |
| :--- | :--- | :--- |
| `use_notebook` | Connects to or creates a new notebook and activates it. | `notebook_name`, `notebook_path`, `mode` ("connect" or "create") |
| `insert_execute_code_cell` | Shortcut to insert a cell and execute it immediately. | `cell_index`, `cell_source`, `timeout` |
| `execute_cell` | Executes an existing cell and returns outputs (text, HTML, images). | `cell_index`, `timeout`, `stream` |
| `read_notebook` | Returns the structure and content of the notebook. | `notebook_name`, `response_format` ("brief" or "detailed") |
| `list_files` | Lists files in the Jupyter server's file system. | `path`, `max_depth`, `pattern` |

## Implementation Strategy for User Requirements

1.  **Notebook Creation & Persistence**: Use `use_notebook` with `mode="create"` to start a new analysis session. The `notebook_path` ensures the file is saved in the specified folder.
2.  **Automated EDA**: The **EDA Agent** will use `insert_execute_code_cell` to run blocks of code for descriptive statistics and visualization.
3.  **Image Handling**: `execute_cell` returns `ImageContent`, which the agent can then process (e.g., save to a folder, describe for RAG).
4.  **Predictive Modeling**: The **Predictive Modeling Agent** will similarly use `insert_execute_code_cell` to train models and evaluate them.
5.  **Future Reference**: Since the notebooks are saved to the file system via the Jupyter server, they are naturally persisted for future reference as requested by the user.

## References
- [Jupyter MCP Server Documentation](https://jupyter-mcp-server.datalayer.tech/)
- [Jupyter MCP Tools Overview](https://jupyter-mcp-server.datalayer.tech/tools/)
