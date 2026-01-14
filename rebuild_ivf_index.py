"""
Script to rebuild FAISS index with IVF clustering.
Usage: python rebuild_ivf_index.py
"""
import os

# Set environment variable BEFORE importing config
os.environ['VECTOR_INDEX_TYPE'] = 'ivf'
os.environ['IVF_NLIST'] = '64'
os.environ['IVF_NPROBE'] = '8'

from src.ingestion.indexer import VectorIndexer
from src.config import AppConfig

if __name__ == "__main__":
    print("=" * 60)
    print("Rebuilding FAISS Index with IVF Clustering")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  VECTOR_INDEX_TYPE: {AppConfig.VECTOR_INDEX_TYPE}")
    print(f"  IVF_NLIST: {AppConfig.IVF_NLIST}")
    print(f"  IVF_NPROBE: {AppConfig.IVF_NPROBE}")
    print(f"  Factory String: {AppConfig.get_index_factory_string()}")
    print()

    VectorIndexer.rebuild_index()

    print("\n" + "=" * 60)
    print("Index rebuild complete!")
    print("=" * 60)
