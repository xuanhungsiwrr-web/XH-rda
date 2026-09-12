"""Prefer the plugin-local venv, otherwise the explicitly configured host Python."""
import os
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
python = root / ('.venv/Scripts/python.exe' if os.name == 'nt' else '.venv/bin/python')
os.environ['PYTHONUTF8'] = '1'
os.execv(str(python) if python.exists() else sys.executable,
         [str(python) if python.exists() else sys.executable, str(root/'scripts/xh_mcp_server.py')])
