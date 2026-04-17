from __future__ import annotations

import sys
from pathlib import Path


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[3] / "pipeline-framework" / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.runtime.runtime_config import RuntimeConfig, RuntimeMode, VALID_RUNTIME_MODES, build_runtime_config, parse_runtime_mode  # noqa: E402,F401
