from typing import Any, Optional, List
from crewai import Agent, Task
from crewai.tools import tool, BaseTool
from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.rag_manager import RAGManager
from mcp_clients.jupyter_client import JupyterMCPClient

logger = get_logger(__name__)

class PredictiveModelingAgent(BaseAgent):
    """
    Agent specialized in building and evaluating machine learning models.
    """

    def __init__(
        self,
        rag_manager: Optional[RAGManager] = None,
        jupyter_client: Optional[JupyterMCPClient] = None,
        **kwargs: Any
    ):
        self.rag_manager = rag_manager
        self.jupyter_client = jupyter_client
        
        # Initialize tools
        tools = self._create_tools()

        super().__init__(
            role="Predictive Modeling Specialist",
            goal="Build, train, and evaluate accurate machine learning models.",
            backstory="""You are an expert machine learning engineer. You specialize in 
            scikit-learn, XGBoost, and model evaluation. You prefer to write clean, 
            efficient Python code to train models and report metrics like RMSE, AUC, or Accuracy.""",
            tools=tools,
            **kwargs
        )

    def _create_tools(self) -> List[BaseTool]:
        tools = []
        
        # RAG Tools
        if self.rag_manager:
            @tool("Read Analysis Context")
            def read_context(query: str) -> str:
                """Read EDA insights and data schema from knowledge base."""
                try:
                    results = self.rag_manager.query(query, n_results=3)
                    if isinstance(results, dict) and 'documents' in results and results['documents']:
                         return "\n".join(results['documents'][0])
                    return "No context found."
                except Exception as e:
                    return f"Error reading context: {e}"

            tools.append(read_context)

        # Jupyter Tools
        if self.jupyter_client:
            @tool("Train Model via Python")
            def train_model(code: str) -> str:
                """Execute Python code to train models (sklearn/xgboost). Access data loaded in previous steps."""
                try:
                    # Reuse the same notebook session "analysis_session.ipynb"
                    notebook_name = "analysis_session.ipynb"
                    self.jupyter_client.use_notebook(notebook_name)
                    
                    # Execute code
                    result = self.jupyter_client.insert_execute_code_cell(cell_index=0, cell_source=code)
                    
                    # Format output
                    return str(result)
                except Exception as e:
                    return f"Error training model: {e}"
            
            tools.append(train_model)
            
        return tools
