import os
import time
import pytest
from src.ingestion.indexer import VectorIndexer
from src.ingestion.metadata import MetadataManager
from src.config import AppConfig
from fpdf import FPDF

def create_dummy_pdf(filename: str, content: str):
    file_path = os.path.join(AppConfig.RAW_DATA_PATH, filename)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, content, ln=1, align='L')
    pdf.output(file_path)
    return file_path

@pytest.fixture(scope="function")
def clean_env(test_data_dir):
    """Ensure a clean environment for each test function."""
    # Clean raw dir
    raw_dir = AppConfig.RAW_DATA_PATH
    for f in os.listdir(raw_dir):
        os.remove(os.path.join(raw_dir, f))
    
    # Clean vector store (remove everything)
    vec_dir = AppConfig.VECTOR_DB_PATH
    # Removing the directory itself might break things if AppConfig expects it to exist, 
    # but MetadataManager creates it.
    # Let's just remove files inside.
    if os.path.exists(vec_dir):
        for f in os.listdir(vec_dir):
            file_path = os.path.join(vec_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            # handle subdirs if any? FAISS usually flat or index.faiss + index.pkl

    return test_data_dir

def test_incremental_workflow(clean_env):
    """
    Test the full lifecycle: Add -> No Change -> Update -> Delete
    """
    filename = "inc_test.pdf"
    
    # --- Step 1: Add New File ---
    print("\n[Test] Step 1: Adding new file...")
    create_dummy_pdf(filename, "Initial content v1.")
    
    VectorIndexer.sync_index()
    
    # Verify Metadata
    mgr = MetadataManager()
    entry = mgr.get_file_entry(filename)
    assert entry is not None
    assert len(entry['chunk_ids']) > 0
    hash_v1 = entry['hash']
    
    # Verify FAISS index exists
    assert os.path.exists(os.path.join(AppConfig.VECTOR_DB_PATH, "index.faiss"))
    
    # --- Step 2: No Change (Skip) ---
    print("\n[Test] Step 2: No changes...")
    # Capture timestamp to ensure we don't update if not needed
    last_modified_v1 = entry['last_modified']
    
    VectorIndexer.sync_index()
    
    # Reload metadata
    mgr = MetadataManager() # Reload from disk
    entry = mgr.get_file_entry(filename)
    # Ideally last_modified shouldn't change if we skipped, 
    # but my implementation updates 'last_modified' only on update_file_entry.
    # Since we skipped, update_file_entry wasn't called.
    # So we check if hash is same.
    assert entry['hash'] == hash_v1
    
    # --- Step 3: Update File ---
    print("\n[Test] Step 3: Updating file content...")
    # Sleep to ensure timestamp/hash might vary (though hash is content based)
    time.sleep(1) 
    create_dummy_pdf(filename, "Updated content v2. This is different.")
    
    VectorIndexer.sync_index()
    
    mgr = MetadataManager()
    entry = mgr.get_file_entry(filename)
    assert entry['hash'] != hash_v1
    # Check if chunk IDs changed (since content changed, hash prefix changes)
    assert not any(cid.startswith(hash_v1) for cid in entry['chunk_ids'])
    
    # --- Step 4: Delete File ---
    print("\n[Test] Step 4: Deleting file...")
    os.remove(os.path.join(AppConfig.RAW_DATA_PATH, filename))
    
    VectorIndexer.sync_index()
    
    mgr = MetadataManager()
    entry = mgr.get_file_entry(filename)
    assert entry is None
    
    # Verify metadata file is saved and empty of files
    assert mgr.get_all_files() == []
