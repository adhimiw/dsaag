"""EDA & RAG Agent for data analysis and knowledge retrieval."""

from typing import Any, List, Optional

from crewai import Agent
from crewai.tools import BaseTool, tool

from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.rag_manager import RAGManager
# Import Jupyter client if needed for type hinting, though use Any to avoid circular ref issues if any
from mcp_clients.jupyter_client import JupyterMCPClient

logger = get_logger(__name__)


class EdaRagAgent(BaseAgent):
    """Agent for Exploratory Data Analysis and RAG queries."""

    def __init__(
        self,
        rag_manager: Optional[RAGManager] = None,
        jupyter_client: Optional[JupyterMCPClient] = None,
        **kwargs: Any
    ):
        """Initialize EDA & RAG Agent.

        Args:
            rag_manager: Optional RAGManager instance
            jupyter_client: Optional JupyterMCPClient instance
            **kwargs: Additional arguments
        """
        role = "EDA and Knowledge Specialist"
        goal = "Analyze datasets, generate insights, and retrieve relevant information from the knowledge base"
        backstory = """You are an expert data analyst and researcher.
        You are skilled at exploring datasets to find patterns, anomalies, and insights.
        You also have access to a vast knowledge base which you can query to support your analysis with context.
        You combine quantitative analysis with qualitative knowledge retrieval.
        You can execute Python code to perform complex calculations and data manipulations."""
        
        self.rag_manager = rag_manager
        self.jupyter_client = jupyter_client

        # Initialize tools
        tools = self._create_tools()

        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            **kwargs
        )

        logger.info("EDA & RAG Agent initialized")

    def _create_tools(self) -> List[BaseTool]:
        """Create tools for the agent.

        Returns:
            List of tools
        """
        tools = []
        
        if self.rag_manager:
            @tool("Query Knowledge Base")
            def query_knowledge_base(query: str) -> str:
                """Query the internal knowledge base for information.
                Useful for finding context, historical data, or explanations related to the analysis.
                Args:
                    query: The question or search term to look up.
                """
                # Use self.rag_manager via closure or self if method is bound?
                # Using self.rag_manager (instance attribute) directly if method is bound correctly?
                # No, better capture 'rag_manager' local var or self.rag_manager from outer scope.
                # However, `create_tools` is an instance method.
                # Let's use `self.rag_manager` but since this is a nested function, it captures `self`.
                
                results = self.rag_manager.query(query_text=query, n_results=3)
                
                if not results or not results.get('documents'):
                    return "No relevant information found in the knowledge base."
                
                # Format results
                docs = results['documents'][0]
                metadatas = results['metadatas'][0] if results.get('metadatas') else [{}] * len(docs)
                
                formatted_results = []
                for i, (doc, meta) in enumerate(zip(docs, metadatas)):
                    source = meta.get('source', 'Unknown') if meta else 'Unknown'
                    formatted_results.append(f"Result {i+1} (Source: {source}):\n{doc}\n")
                    
                return "\n".join(formatted_results)

            tools.append(query_knowledge_base)
        
        if self.jupyter_client:
             @tool("Execute Python Code")
             def execute_code(code: str) -> str:
                """Execute Python code in a Jupyter notebook environment.
                Useful for data analysis, calculations, and visualization.
                Args:
                    code: Valid Python code block to execute.
                """
                try:
                    # Initialize/Get notebook connection
                    # We use a standard name for the analysis session
                    notebook_name = "analysis_session.ipynb"
                    self.jupyter_client.use_notebook(notebook_name)
                    
                    # Execute code
                    # Insert at index 0 (top) or create new cell. 
                    # Assuming insert_execute_code_cell supports executing.
                    # We use cell_index=0 to prepend, or we could track index.
                    # For a running history, appending (effectively) is better, but Jupyter API usually requires index.
                    # A safe bet is using index=0 then it shifts others down, effectively a "console" at top?
                    # Or we just use index=1000 to append.
                    # Let's try inserting at top for visibility.
                    result = self.jupyter_client.insert_execute_code_cell(cell_index=0, cell_source=code)
                    
                    # Format output
                    # Result structure depends on MCP server, usually has 'output' or similar.
                    # BaseMCPClient call_tool returns the raw dict.
                    return str(result)
                except Exception as e:
                    return f"Error executing code in Jupyter: {e}"

             tools.append(execute_code)

        return tools
