"""Test configuration for AutoML repository.

Ensures the repository root is on ``sys.path`` so that helper modules like
``automl`` can be imported regardless of the working directory.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
