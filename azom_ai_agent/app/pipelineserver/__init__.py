"""Initialization for pipelineserver package.

Ensures that the project root is on sys.path so that absolute imports like
`import app.logger` work when `pipeline_app` is executed as a top-level package
(e.g. in unit tests that do `from pipeline_app.main import app`).
"""
import pathlib
import sys as _sys

# Add the repository root (two levels up from this file) to `sys.path`
_root = pathlib.Path(__file__).resolve().parents[2]
if str(_root) not in _sys.path:
    _sys.path.append(str(_root))
