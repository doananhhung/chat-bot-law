import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from src.config import AppConfig
from src.utils.logger import logger

class MetadataManager:
    """Manages the file registry for incremental indexing."""

    def __init__(self, metadata_path: str = None):
        if metadata_path is None:
            # Default to tracking inside the vector_store directory
            metadata_path = os.path.join(AppConfig.VECTOR_DB_PATH, "indexing_metadata.json")
        
        self.metadata_path = metadata_path
        self.data = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load metadata from JSON file."""
        if not os.path.exists(self.metadata_path):
            return {"last_updated": None, "files": {}}
        
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {"last_updated": None, "files": {}}

    def save_metadata(self):
        """Save metadata to JSON file."""
        self.data["last_updated"] = datetime.utcnow().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def get_file_entry(self, filename: str) -> Optional[Dict]:
        """Get metadata for a specific file."""
        return self.data["files"].get(filename)

    def update_file_entry(self, filename: str, file_hash: str, chunk_ids: List[str]):
        """Update or add a file entry."""
        self.data["files"][filename] = {
            "hash": file_hash,
            "last_modified": datetime.utcnow().timestamp(), # or os.path.getmtime
            "chunk_ids": chunk_ids
        }

    def remove_file_entry(self, filename: str):
        """Remove a file entry."""
        if filename in self.data["files"]:
            del self.data["files"][filename]

    def get_all_files(self) -> List[str]:
        """Get list of all tracked filenames."""
        return list(self.data["files"].keys())

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except FileNotFoundError:
            return ""
