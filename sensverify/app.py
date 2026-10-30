"""
SensVerify Subdirectory Entry Point
Enables deployments where Root Directory or Path is set to 'sensverify'.
"""
import runpy
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

parent_app = root_dir / "app.py"
runpy.run_path(str(parent_app), run_name="__main__")
