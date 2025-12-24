import os
from typing import List, Dict, Any
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from src.utils.logger import logger
from dataclasses import dataclass

@dataclass
class LoadResult:
    documents: List[Document]
    failed_files: List[Dict[str, str]]

class DocumentLoader:
    """Handles loading of documents from a directory."""
    
    SUPPORTED_EXTENSIONS = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".doc": Docx2txtLoader
    }
    
    @staticmethod
    def load_single_file(file_path: str) -> List[Document]:
        """
        Load a single supported document.
        """
        path_obj = Path(file_path)
        if not path_obj.exists() or not path_obj.is_file():
            logger.warning(f"File not found: {file_path}")
            return []
            
        ext = path_obj.suffix.lower()
        if ext not in DocumentLoader.SUPPORTED_EXTENSIONS:
            logger.debug(f"Skipping unsupported file: {path_obj.name}")
            return []
            
        loader_cls = DocumentLoader.SUPPORTED_EXTENSIONS[ext]
        try:
            logger.info(f"Loading file: {path_obj.name}")
            loader = loader_cls(str(path_obj))
            docs = loader.load()
            
            # Enhance metadata
            for doc in docs:
                doc.metadata["source"] = path_obj.name
                if "page" not in doc.metadata:
                    doc.metadata["page"] = 0
            
            return docs
            
        except Exception as e:
            logger.error(f"Failed to load {path_obj.name}: {str(e)}")
            return []

    @staticmethod
    def load_documents(directory_path: str) -> LoadResult:
        """
        Load all supported documents from the specified directory.
        """
        documents: List[Document] = []
        failed_files: List[Dict[str, str]] = []
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            logger.warning(f"Directory not found: {directory_path}")
            return LoadResult(documents=[], failed_files=[])
            
        files = [f for f in dir_path.iterdir() if f.is_file()]
        logger.info(f"Found {len(files)} files in {directory_path}")
        
        for file_path in files:
            ext = file_path.suffix.lower()
            
            if ext not in DocumentLoader.SUPPORTED_EXTENSIONS:
                logger.debug(f"Skipping unsupported file: {file_path.name}")
                continue
                
            loader_cls = DocumentLoader.SUPPORTED_EXTENSIONS[ext]
            
            try:
                logger.info(f"Loading file: {file_path.name}")
                loader = loader_cls(str(file_path))
                docs = loader.load()
                
                # Enhance metadata
                for doc in docs:
                    doc.metadata["source"] = file_path.name
                    # Ensure page is present (PyPDF adds it, Docx might not)
                    if "page" not in doc.metadata:
                        doc.metadata["page"] = 0
                        
                documents.extend(docs)
                
            except Exception as e:
                logger.error(f"Failed to load {file_path.name}: {str(e)}")
                failed_files.append({"file": file_path.name, "reason": str(e)})
                
        logger.info(f"Successfully loaded {len(documents)} document chunks/pages.")
        return LoadResult(documents=documents, failed_files=failed_files)
