from typing import Any, Optional, List
from crewai import Agent, Task
from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.rag_manager import RAGManager
from llm.base_llm import BaseLLM

logger = get_logger(__name__)

class AnalysisDecisionAgent(BaseAgent):
    """
    Agent responsible for deciding between descriptive/EDA and predictive analysis.
    It analyzes data schema and quality from RAG and user intent.
    """

    def __init__(
        self,
        rag_manager: Optional[RAGManager] = None,
        **kwargs: Any
    ):
        super().__init__(
            role="Analysis Decision Maker",
            goal="Determine if the dataset and user intent are suitable for predictive modeling.",
            backstory="""You are a senior data science strategist. Your job is to evaluate 
            if a machine learning model should be built. You look at the data availability, 
            quality, and the user's request. You are conservative - you only recommend 
            predictive modeling if there is a clear target and sufficient data quality.""",
            **kwargs
        )
        self.rag_manager = rag_manager

    def decide_analysis_type(self, user_request: str) -> str:
        """
        Decides whether to perform 'descriptive' or 'predictive' analysis.
        Returns: 'predictive' or 'descriptive'
        """
        # 1. Retrieve Context from RAG (Schema, EDA Insights)
        context = ""
        if self.rag_manager:
            try:
                # Query for schema and insights
                results = self.rag_manager.query("data schema column names target variable data quality missing values", n_results=5)
                context = "\n".join(results)
            except Exception as e:
                logger.warning(f"Failed to query RAG for decision context: {e}")

        # 2. logical check via LLM
        prompt = f"""
        User Request: "{user_request}"
        
        Available Data Context from RAG:
        {context}
        
        Task: Decide whether to proceed with Predictive Modeling or stick to Descriptive Analysis (EDA).
        
        Criteria for Predictive Modeling:
        1. User explicitly asks for prediction/forecasting.
        2. OR There is a clear target variable mentioned in the context AND data quality seems sufficient (no critical issues mentioned).
        
        Criteria for Descriptive Analysis:
        1. User only asks for summary, visualization, or 'what happened'.
        2. OR Data is insufficient, unstructured, or lacks a target.
        
        Response Format:
        Just return one word: 'PREDICTIVE' or 'DESCRIPTIVE'.
        """
        
        response = self.llm.generate(prompt)
        decision = response.strip().upper()
        
        if "PREDICTIVE" in decision:
            return "predictive"
        return "descriptive"

    def _create_tools(self) -> List[Any]:
        # This agent primarily uses internal logic and RAG, 
        # but could expose a 'check_feasibility' tool if needed by other agents.
        return []
