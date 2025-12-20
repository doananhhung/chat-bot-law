import uuid
from datetime import datetime
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import AppConfig
from src.utils.logger import logger

class TextSplitter:
    """Handles splitting of documents into smaller chunks."""
    
    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks and add metadata.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=AppConfig.CHUNK_SIZE,
            chunk_overlap=AppConfig.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Split documents
        # Note: This might lose the grouping of which chunks belong to which original document 
        # if we just pass the whole list. 
        # To calculate 'total_chunks' per document correctly, we should split per original document 
        # or group them by source/page. 
        # However, a simpler approach for MVP is to process them, but to get total_chunks per file, 
        # we really need to split file by file.
        
        # Let's try to group by source file to be accurate with 'total_chunks' if possible, 
        # but 'documents' passed here are already pages (from PyPDFLoader). 
        # So 'one document' in the input list is actually 'one page'.
        # Merging them back to 'one file' to split might be better for context, 
        # but PyPDFLoader usage implies page-based chunks initially.
        
        # For this implementation, I will treat the input list as the stream of content 
        # and split them. If we want 'total_chunks' per original file, it's complex because 
        # the input is already fragmented by pages.
        
        # A workaround strictly following the spirit of "Robust RAG":
        # We process the split, then we can iterate to assign IDs.
        
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} input docs into {len(split_docs)} chunks.")
        
        # Post-process for metadata
        # We need to group by source to calculate total_chunks per source if we want that metric,
        # but here we might just count global or simple index.
        # The design asks for 'chunk_index' and 'total_chunks'.
        # Let's group by 'source' to count.
        
        docs_by_source = {}
        for doc in split_docs:
            source = doc.metadata.get("source", "unknown")
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
            
        final_docs = []
        created_at = datetime.utcnow().isoformat() + "Z"
        
        for source, source_docs in docs_by_source.items():
            total = len(source_docs)
            for idx, doc in enumerate(source_docs):
                doc.metadata.update({
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_index": idx,
                    "total_chunks": total,
                    "created_at": created_at
                })
                final_docs.append(doc)
                
        return final_docs
