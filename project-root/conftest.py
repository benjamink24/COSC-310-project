import sys
from pathlib import Path
import os

os.environ["RUNNING_TESTS"] = "1"

root = Path(__file__).parent
sys.path.insert(0, str(root / "app"))