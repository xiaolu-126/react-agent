
"""Pytest configuration and shared fixtures.
"""
import pytest
import sys
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def project_root():
    """Return the project root directory path."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir(tmp_path):
    """Return a temporary directory path."""
    return tmp_path


@pytest.fixture
def sample_config():
    """Return a sample configuration dictionary."""
    return {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2048
    }

