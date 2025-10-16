import pytest
import sys
import os

# Add parent dir to path so tests can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
