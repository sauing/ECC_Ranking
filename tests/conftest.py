import os
import sys

# Add repository root to sys.path so tests can import ecc_rankings
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

