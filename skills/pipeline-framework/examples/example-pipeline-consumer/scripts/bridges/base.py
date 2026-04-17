from __future__ import annotations

import sys
from pathlib import Path


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[4] / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.bridges.base import execute_provider  # noqa: E402,F401
