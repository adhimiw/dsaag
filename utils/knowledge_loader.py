"""Utility to load project documentation into the RAG system."""

import glob
import os
from pathlib import Path
from typing import List

from utils.logger import get_logger
from utils.rag_manager import RAGManager

logger = get_logger(__name__)


class KnowledgeLoader:
    """Loader for populating the knowledge base with project documents."""

    def __init__(self, rag_manager: RAGManager):
        """Initialize Knowledge Loader.

        Args:
            rag_manager: RAG Manager instance
        """
        self.rag_manager = rag_manager
        self.settings = rag_manager.settings

    def load_markdown_files(self, directory: str = ".") -> int:
        """Load Markdown files from a directory into the knowledge base.

        Args:
            directory: Root directory to search (relative to project root)

        Returns:
            Number of documents added
        """
        search_path = os.path.join(self.settings.project_root, directory, "*.md")
        files = glob.glob(search_path)
        
        if not files:
            logger.warning(f"No markdown files found in {search_path}")
            return 0

        documents = []
        metadatas = []
        ids = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                filename = os.path.basename(file_path)
                
                # Simple chunking by paragraph or just one blob for now
                # For documentation, splitting by large sections might be better, 
                # but for simplicity we'll store the whole file if small, or chunks
                
                # Basic chunking strategy: Split by headers
                # For now, let's just add the whole file content to keep it simple for high-level context
                # In a real app, we'd use a proper text splitter
                
                documents.append(content)
                metadatas.append({"source": filename, "type": "documentation"})
                ids.append(filename) # Use filename as ID to avoid duplicates
                
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")

        if documents:
            logger.info(f"Loading {len(documents)} documents into RAG...")
            # ChromaDB's add method handles upsert if IDs are provided? 
            # Actually, `add` might fail on duplicates. `upsert` is safer.
            try:
                self.rag_manager.collection.upsert(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info("Documents loaded successfully")
                return len(documents)
            except Exception as e:
                logger.error(f"Error upserting documents: {e}")
                return 0
        
        return 0
