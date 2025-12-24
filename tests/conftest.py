import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import shutil
from fpdf import FPDF
from src.config import AppConfig

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    base_dir = Path(__file__).parent / "temp_data"
    raw_dir = base_dir / "raw"
    vector_dir = base_dir / "vector_store"
    
    # Clean up before start
    if base_dir.exists():
        shutil.rmtree(base_dir)
    
    os.makedirs(raw_dir)
    os.makedirs(vector_dir)
    
    # Mock AppConfig paths for testing
    original_raw = AppConfig.RAW_DATA_PATH
    original_vector = AppConfig.VECTOR_DB_PATH
    
    AppConfig.RAW_DATA_PATH = str(raw_dir)
    AppConfig.VECTOR_DB_PATH = str(vector_dir)
    
    yield base_dir
    
    # Cleanup after tests
    # Restore Config (though process dies anyway)
    AppConfig.RAW_DATA_PATH = original_raw
    AppConfig.VECTOR_DB_PATH = original_vector
    
    if base_dir.exists():
        shutil.rmtree(base_dir)

@pytest.fixture(scope="session")
def dummy_pdf(test_data_dir):
    """Create a dummy PDF file for testing."""
    filename = "test_doc.pdf"
    file_path = Path(AppConfig.RAW_DATA_PATH) / filename
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "This is a test document for unit testing.", ln=1, align='L')
    pdf.cell(200, 10, "It contains legal information about AI testing.", ln=1, align='L')
    pdf.output(str(file_path))
    
    return str(file_path)