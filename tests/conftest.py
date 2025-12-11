import os
import sys

# doda katalog projektu/src do sys.path tak, aby importy "from src..." działały
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
