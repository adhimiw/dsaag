"""RAG Manager for handling vector store operations using ChromaDB."""

import os
from typing import Any, List, Optional
import chromadb
from chromadb.utils import embedding_functions

from config import get_settings
from llm.base_llm import BaseLLM
from utils.logger import get_logger

logger = get_logger(__name__)


class RAGManager:
    """Manager for RAG operations using ChromaDB."""

    def __init__(self, llm: BaseLLM, fallback_llm: Optional[BaseLLM] = None):
        """Initialize RAG Manager.

        Args:
            llm: LLM instance to use for embeddings
            fallback_llm: Optional fallback LLM for embeddings
        """
        self.llm = llm
        self.fallback_llm = fallback_llm
        self.settings = get_settings()
        
        # Ensure data directory exists
        db_path = os.path.join(self.settings.data_dir, "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize Client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Define embedding function using our LLM
        # We need to wrap our LLM's embed method to match ChromaDB's interface
        self.embedding_fn = self._create_embedding_function()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.embedding_fn
        )
        
        logger.info(f"RAG Manager initialized with ChromaDB at {db_path}")

    def _create_embedding_function(self):
        """Create an embedding function compatible with ChromaDB."""
        
        # Capture self.llm and self.fallback_llm
        primary = self.llm
        fallback = self.fallback_llm
        
        class LLMEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
                # LLM's embed method processes a list of strings and returns list of embeddings
                try:
                    return primary.embed(input)
                except Exception as e:
                    logger.error(f"Error generating embeddings with primary LLM: {e}")
                    if fallback:
                        logger.info("Attempting fallback LLM for embeddings...")
                        try:
                            return fallback.embed(input)
                        except Exception as e2:
                            logger.error(f"Error generating embeddings with fallback LLM: {e2}")
                            raise e
                    else:
                        raise e
                
        return LLMEmbeddingFunction()

    def add_documents(
        self, 
        documents: List[str], 
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the knowledge base.

        Args:
            documents: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of IDs. If None, they will be generated.
        """
        if not documents:
            return

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to knowledge base")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise

    def query(
        self, 
        query_text: str, 
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> dict:
        """Query the knowledge base.

        Args:
            query_text: Query string
            n_results: Number of results to return
            where: Optional filtering criteria

        Returns:
            Query results from ChromaDB
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return {}
