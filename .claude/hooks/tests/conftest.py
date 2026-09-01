from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
ADAPTER_SOURCE = REPO_ROOT / ".grok" / "hooks" / "grok_hook_adapter.py"
HOOKS_SOURCE = REPO_ROOT / ".claude" / "hooks"


@pytest.fixture
def isolated_repo(tmp_path: Path) -> Path:
    adapter_dir = tmp_path / ".grok" / "hooks"
    hooks_dir = tmp_path / ".claude" / "hooks"
    adapter_dir.mkdir(parents=True)
    hooks_dir.mkdir(parents=True)
    shutil.copy2(ADAPTER_SOURCE, adapter_dir / ADAPTER_SOURCE.name)
    for hook_path in HOOKS_SOURCE.glob("*.py"):
        shutil.copy2(hook_path, hooks_dir / hook_path.name)
    return tmp_path


@pytest.fixture
def adapter_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("grok_hook_adapter", ADAPTER_SOURCE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def run_adapter(
    isolated_repo: Path,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    adapter_path = isolated_repo / ".grok" / "hooks" / ADAPTER_SOURCE.name

    def run(
        *,
        handler: str,
        event: str,
        payload: dict[str, Any] | str,
        extra_environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        for name in (
            "CLAUDE_ALLOW_SECRET_WRITE",
            "CLAUDE_PROJECT_DIR",
            "GROK_HOOK_EVENT",
            "GROK_HOOK_NAME",
            "GROK_SESSION_ID",
            "GROK_WORKSPACE_ROOT",
        ):
            environment.pop(name, None)
        if extra_environment:
            environment.update(extra_environment)
        raw_payload = (
            payload if isinstance(payload, str) else __import__("json").dumps(payload)
        )
        return subprocess.run(
            [
                sys.executable,
                str(adapter_path),
                "--event",
                event,
                "--handler",
                handler,
            ],
            input=raw_payload,
            text=True,
            capture_output=True,
            check=False,
            cwd=isolated_repo,
            env=environment,
        )

    return run
