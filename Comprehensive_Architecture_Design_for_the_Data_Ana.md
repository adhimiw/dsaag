# Comprehensive Architecture Design for the Data Analytics Agent

The proposed system is a sophisticated, multi-agent data analytics platform designed to automate the entire data science workflow, from data ingestion and exploratory analysis (EDA) to predictive modeling and intelligent, context-aware conversational querying. The architecture is built upon the **Model Context Protocol (MCP)** for tool integration and a **Retrieval-Augmented Generation (RAG)** system for memory and context.

## 1. Multi-Agent Orchestration (CrewAI Framework)

The system employs a multi-agent architecture, orchestrated by a **Supervisor Agent**, to ensure complex tasks are broken down and executed efficiently. This design is based on the principles of the CrewAI framework, which facilitates structured collaboration between specialized agents.

| Agent Role | Primary Function | Key Tools (MCP Servers) | RAG Interaction |
| :--- | :--- | :--- | :--- |
| **Supervisor Agent** | Orchestrates the entire workflow, delegates tasks, and synthesizes final results. **Triggers the Analysis Decision Logic after Data Ingestion.** | None (Orchestration) | Reads RAG for final context synthesis. |
| **Data Ingestion Agent** | Loads user-provided data, performs initial cleaning, validation, and feature type identification. | Terminal MCP (for file operations) | Writes initial data schema and cleaning log to RAG. |
| **EDA & RAG Agent** | Performs descriptive statistics, generates visualizations (EDA), and extracts key insights. | **Jupyter MCP Server** (Code Execution, Visualization) | Writes descriptive statistics, key insights, and image captions/metadata to RAG. |
| **Analysis Decision Agent** | **NEW: Autonomously determines if the dataset is suitable for Predictive Analysis based on heuristics (target variable, data quality) and user intent.** If suitable, triggers the Predictive Modeling Agent. | None (LLM Reasoning) | Reads RAG for Data Schema and EDA Insights. |
| **Predictive Modeling Agent** | Performs feature engineering, model training, evaluation, and selection (e.g., using H2O.ai). Only runs if triggered by the Analysis Decision Agent. | **Jupyter MCP Server** (Code Execution, Modeling) | Writes model summary, feature importance, and evaluation metrics to RAG. |
| **Web Research Agent** | Executes external searches (Google, Reddit scraping) to gather real-world context for chat queries. | **Browser MCP Server** (Web Navigation, Search, Scraping) | Writes retrieved external context (e.g., news articles, Reddit threads) to RAG for immediate use. |
| **Conversational Agent** | The user-facing interface. Answers questions based on internal analysis and external context. | None (LLM Reasoning) | **Primary RAG Consumer**: Queries RAG for all internal analysis context before generating a response. Triggers Web Research Agent if context is insufficient. |

## 1.1 Autonomous Analysis Decision Logic

To fulfill the requirement that the agent must autonomously decide between descriptive and predictive analysis, a dedicated **Analysis Decision Agent** is introduced. This agent operates after the initial data ingestion and preliminary EDA, using a set of heuristics and LLM-based reasoning to make a grounded decision.

The decision logic is as follows:

1.  **Target Variable Check**: The agent queries the RAG for the Data Schema (provided by the Data Ingestion Agent) to check for the presence of a clearly defined, non-null column that could serve as a target variable (e.g., a binary column like `is_churn`, a continuous column like `price`, or a time-series column).
2.  **Data Quality Assessment**: The agent reviews the EDA Insights (provided by the EDA & RAG Agent) for critical data quality issues, such as excessive missing values in key features or a lack of variance in the potential target variable.
3.  **User Intent Override**: The agent checks the initial user request. If the user explicitly asked for a prediction (e.g., "Predict the sales for next quarter"), the agent will prioritize the predictive path, provided the Target Variable Check is positive.

If the Target Variable Check is positive and the Data Quality Assessment is acceptable, the agent proceeds with the **Predictive Modeling Agent**. Otherwise, the analysis concludes with the descriptive findings from the **EDA & RAG Agent**, and the **Conversational Agent** is informed that the dataset is not suitable for predictive modeling.

## 2. Model Context Protocol (MCP) Tool Layer

The MCP layer is critical for providing the agents with the ability to interact with the execution environment and the external world.

### 2.1 Jupyter Notebook MCP Server

This server, based on the `datalayer/jupyter-mcp-server` implementation, is the execution engine for the analytical agents.

*   **Functionality**: Allows the **EDA & RAG Agent** and the **Predictive Modeling Agent** to execute Python code, run data analysis libraries (Pandas, Matplotlib, Scikit-learn, H2O.ai), and generate visualizations within a controlled Jupyter environment.
*   **Output**: The server facilitates the saving of the executed notebook (`.ipynb`) and all generated EDA images to a designated project folder, fulfilling the user's requirement for saving data for future reference.

### 2.2 Browser MCP Server

This server provides the necessary web interaction capabilities for the **Web Research Agent**.

*   **Functionality**: Enables the agent to perform Google searches and navigate to specific sites like Reddit for scraping, simulating human-like web research. This is crucial for answering questions that require external, real-time context (e.g., "Why did Taylor Swift's song drop in popularity?").
*   **Implementation**: This can be implemented using the **Chrome DevTools MCP** for high-fidelity browser control, or a specialized **Scrapeless MCP Server** for structured search results and scraping. The design will prioritize the high-fidelity approach for flexibility.

## 3. Retrieval-Augmented Generation (RAG) Memory System

The RAG system serves as the agent's long-term and short-term memory, ensuring the **Conversational Agent** can provide accurate, context-grounded answers based on the analysis performed.

### 3.1 RAG Data Structure

The RAG memory will be a vector database storing embeddings of structured and unstructured data generated throughout the analysis workflow.

| Data Type | Source Agent | Content Stored in RAG | Purpose |
| :--- | :--- | :--- | :--- |
| **Data Schema** | Data Ingestion Agent | Column names, data types, missing value counts. | Context for data structure and quality. |
| **Descriptive Statistics** | EDA & RAG Agent | Mean, median, mode, standard deviation, quartiles, correlation matrices. | Factual basis for "what happened" questions. |
| **EDA Insights** | EDA & RAG Agent | Natural language summaries of trends, anomalies, and relationships observed in the data and visualizations. | Context for "why" and "how" questions. |
| **Visualization Metadata** | EDA & RAG Agent | Captions, file paths, and a brief description of each generated EDA image. | Allows the agent to reference specific visual evidence. |
| **Model Summary** | Predictive Modeling Agent | Model type, performance metrics (e.g., R-squared, AUC), and top feature importance. | Context for predictive capabilities and feature impact. |
| **External Context** | Web Research Agent | Snippets from Google Search, scraped Reddit posts, and news articles. | Context for answering questions requiring real-world knowledge. |

### 3.2 RAG Workflow for Conversational Agent

1.  **User Query**: The user asks a question (e.g., "What is the average age of our customers, and why did the sales spike in Q3?").
2.  **RAG Retrieval**: The **Conversational Agent** queries the RAG system with the user's question.
3.  **Context Check**:
    *   **Internal Context Found**: If the RAG returns high-confidence context (e.g., "Average age is 35.2," and "Sales spiked due to a new product launch, as noted in the EDA insights"), the agent generates the answer.
    *   **External Context Needed**: If the RAG returns no relevant internal context but the query suggests external knowledge (e.g., "Why did Taylor Swift's song drop?"), the **Conversational Agent** triggers the **Web Research Agent**.
4.  **Web Research & Update**: The **Web Research Agent** performs the search, writes the findings to the RAG memory, and the **Conversational Agent** re-queries the RAG to generate a comprehensive, grounded answer.

## 4. Implementation Roadmap

The final phase will detail the implementation steps, focusing on setting up the environment, configuring the MCP servers, and developing the agents and RAG system. This design provides a solid foundation for the next phase of detailed planning.
