"""Shared deployed app path and deterministic offline fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = Path(os.environ.get("CC_COPT_APP_PATH", ROOT / "cc_copt/gui.py")).resolve()
APP_ROOT = APP_PATH.parent.parent
SERVER_ARGV = [sys.executable, "-m", "streamlit", "run", "cc_copt/gui.py",
               "--server.port=8501", "--server.address=0.0.0.0",
               "--browser.gatherUsageStats=false"]

@pytest.fixture
def synthetic(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "examples/generate_synthetic.py"),
                    "--out-dir", str(tmp_path), "--seed", "1729"], check=True)
    return tmp_path


def artifact_index(directory):
    """Map container evidence to exact host paths for subsequent reviewers."""
    directory = Path(directory)
    execution = Path("/evidence/execution.json")
    host_root = json.loads(execution.read_text())["run"] if execution.exists() else None
    files = [p for p in directory.rglob("*") if p.is_file() and p.name != "artifacts.json"]
    def host(p):
        if host_root and str(p).startswith("/evidence/"):
            return str(Path(host_root) / p.relative_to("/evidence"))
        return str(p.resolve())
    (directory / "artifacts.json").write_text(json.dumps([host(p) for p in files], indent=2))
