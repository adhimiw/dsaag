"""Main entry point for the Data Analytics Agent."""

import sys
from pathlib import Path

from config import get_settings
from utils.logger import setup_logger, get_logger

# Setup logging first
settings = get_settings()
setup_logger(
    log_level=settings.log_level,
    log_file=settings.log_file,
)

logger = get_logger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting Data Analytics Agent")

    try:
        # Initialize configuration
        settings = get_settings()
        logger.info(f"Configuration loaded: Primary LLM = {settings.primary_llm_provider}")

        # Initialize LLM providers
        from llm.factory import get_llm

        primary_llm = get_llm(provider=settings.primary_llm_provider)
        logger.info(f"Primary LLM initialized: {primary_llm.__class__.__name__}")

        if settings.google_api_key:
            secondary_llm = get_llm(provider="google")
            logger.info(f"Secondary LLM initialized: {secondary_llm.__class__.__name__}")

        # Initialize MCP clients
        from mcp_clients import (
            BrowserMCPClient,
            FilesystemMCPClient,
            JupyterMCPClient,
            TerminalMCPClient,
        )

        filesystem_client = FilesystemMCPClient(
            server_path=settings.filesystem_mcp_server_path,
            transport=settings.mcp_server_transport,
        )
        terminal_client = TerminalMCPClient(
            server_path=settings.terminal_mcp_server_path,
            transport=settings.mcp_server_transport,
        )
        browser_client = BrowserMCPClient(
            server_path=settings.browser_mcp_server_path,
            transport=settings.mcp_server_transport,
        )
        jupyter_client = JupyterMCPClient(
            server_path=settings.jupyter_mcp_server_path,
            transport=settings.mcp_server_transport,
            env={
                "JUPYTER_URL": settings.jupyter_url,
                "JUPYTER_TOKEN": settings.jupyter_token or "",
                "ALLOW_IMG_OUTPUT": "true" 
            }
        )

        logger.info("MCP clients initialized")

        # Create agents
        from agents import DataIngestionAgent, SupervisorAgent, WebResearchAgent

        supervisor = SupervisorAgent(llm=primary_llm)
        data_ingestion = DataIngestionAgent(
            llm=primary_llm,
            filesystem_client=filesystem_client,
            terminal_client=terminal_client,
        )
        web_research = WebResearchAgent(
            llm=primary_llm,
            browser_client=browser_client,
        )

        logger.info("Agents created successfully")

        # Initialize RAG Manager
        # Initialize RAG Manager
        from utils.rag_manager import RAGManager
        secondary_llm_instance = None
        if settings.google_api_key:
             # If secondary LLM was initialized earlier, use it. 
             # However, main.py structure has secondary_llm as a local var.
             # We need to access it.
             # Re-getting it is cheap (singleton/factory) or we can capture it.
             # Let's rely on the factory get_llm which creates new instances but lightweight.
             try:
                secondary_llm_instance = get_llm(provider="google")
             except:
                pass

        rag_manager = RAGManager(llm=primary_llm, fallback_llm=secondary_llm_instance)
        
        # Load initial knowledge base
        from utils.knowledge_loader import KnowledgeLoader
        loader = KnowledgeLoader(rag_manager)
        loader.load_markdown_files()
        
        # Initialize EDA & RAG Agent
        from agents import EdaRagAgent
        eda_rag_agent = EdaRagAgent(
            llm=primary_llm,
            rag_manager=rag_manager,
            jupyter_client=jupyter_client
        )
        logger.info("EDA & RAG Agent initialized")

        # Initialize Phase 3 Agents
        from agents import AnalysisDecisionAgent, PredictiveModelingAgent, ConversationalAgent
        
        analysis_decision_agent = AnalysisDecisionAgent(
            llm=primary_llm, 
            rag_manager=rag_manager
        )
        
        predictive_agent = PredictiveModelingAgent(
            llm=primary_llm,
            rag_manager=rag_manager,
            jupyter_client=jupyter_client
        )
        
        conversational_agent = ConversationalAgent(
            llm=primary_llm,
            rag_manager=rag_manager
        )
        
        logger.info("Phase 3 Agents initialized (Decision, Predictive, Conversational)")

        # Create CrewAI Crew
        from crewai import Crew, Process, Task
        
        # Set OPENAI_API_KEY to prevent CrewAI from erroring during Agent initialization
        import os
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "sk-dummy-key-not-used-for-actual-calls"
            logger.info("Set dummy OPENAI_API_KEY to prevent CrewAI initialization error")

        # Define Verification Tasks
        
        # 0. Data Ingestion (Mocking a dataset)
        import os
        data_path = os.path.join(os.getcwd(), "data", "churn.csv")
        
        task_ingest = Task(
             description=f"""Create a dummy CSV dataset at '{data_path}' with the following content:
id,feature1,feature2,churn
1,0.5,0.1,0
2,0.8,0.9,1
3,0.2,0.3,0
4,0.9,0.9,1
5,0.4,0.2,0
6,0.1,0.1,0
7,0.7,0.8,1
8,0.6,0.6,1
""",
             agent=data_ingestion.get_agent(),
             expected_output=f"Confirmation that file was written to {data_path}"
        )

        # 1. EDA Task
        task_eda = Task(
            description=f"Load the dataset from '{data_path}' using pandas in a Jupyter notebook. Display the first 5 rows and print the columns.",
            agent=eda_rag_agent.get_agent(),
            expected_output="Output showing the head of the dataframe and list of columns."
        )
        
        # 2. Prediction Task
        task_predict = Task(
            description=f"Write and execute a Python script to train a LogisticRegression model on '{data_path}' to predict 'churn'. Use feature1 and feature2 as predictors. Print the accuracy.",
            agent=predictive_agent.get_agent(),
            expected_output="The accuracy score of the trained model."
        )

        crew = Crew(
            agents=[
                data_ingestion.get_agent(),
                eda_rag_agent.get_agent(),
                predictive_agent.get_agent(),
            ],
            tasks=[task_ingest, task_eda, task_predict],
            process=Process.sequential,
            verbose=True,
        )

        logger.info("CrewAI Crew created with Verification Suite")
        logger.info("Data Analytics Agent initialized successfully")
        logger.info("Starting End-to-End Verification: Ingestion -> EDA -> Prediction")
        
        result = crew.kickoff()
        logger.info(f"Verification Result:\n{result}")
        
        return 0

    except Exception as e:
        logger.error("Error initializing agent: {}", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

