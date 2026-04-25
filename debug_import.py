import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from src.processing import classify_hice_type
    print("SUCCESS: classify_hice_type imported")
except ImportError as e:
    print(f"FAILURE: {e}")

import src.processing
print(f"File location: {src.processing.__file__}")
print(f"Attributes in src.processing: {[attr for attr in dir(src.processing) if not attr.startswith('__')]}")
