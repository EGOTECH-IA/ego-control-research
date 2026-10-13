#!/usr/bin/env python3
"""Compatibility runner. Canonical scenario: tests/integration/lab_integration.py."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent / "tests/integration/lab_integration.py"), run_name="__main__")
