from typing import Any, Optional, List
from crewai import Agent, Task
from crewai.tools import tool, BaseTool
from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.rag_manager import RAGManager

logger = get_logger(__name__)

class ConversationalAgent(BaseAgent):
    """
    User-facing agent that answers questions using RAG context.
    """

    def __init__(
        self,
        rag_manager: Optional[RAGManager] = None,
        **kwargs: Any
    ):
        self.rag_manager = rag_manager
        
        # Initialize tools
        tools = self._create_tools()

        super().__init__(
            role="Data Analytics Consultant",
            goal="Provide accurate, context-aware answers to user questions about data and analysis.",
            backstory="""You are a helpful and knowledgeable data consultant. You rely on the 
            internal knowledge base (RAG) to answer questions. You explain complex data findings 
            in simple terms. You always check the knowledge base before answering.""",
            tools=tools,
            **kwargs
        )

    def _create_tools(self) -> List[BaseTool]:
        tools = []
        
        if self.rag_manager:
            class RagTools:
                def __init__(self, manager):
                    self.manager = manager
                
                @tool("Query Knowledge Base")
                def query_knowledge_base(query: str) -> str:
                    """Search the knowledge base for relevant information (EDA insights, model metrics, etc.)."""
                    try:
                        results = self.manager.query(query, n_results=3)
                        if not results:
                            return "No relevant information found in the knowledge base."
                        return "\n\n".join(results)
                    except Exception as e:
                        return f"Error querying knowledge base: {e}"
            
            rag_tools = RagTools(self.rag_manager)
            tools.append(rag_tools.query_knowledge_base)
            
        return tools
