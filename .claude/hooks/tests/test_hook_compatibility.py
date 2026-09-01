from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from conftest import HOOKS_SOURCE


EXPECTED_HOOK_SHA256 = {
    "deploy-gate.py": "a6f93d5842c4e87b9b5574c303b45445e03da6191681c12f0d9e4f11f2073d5e",
    "error-to-codex.py": "58dc0700aa48ff64870ad2849141f07b88bf922f7e824b523bd8cfb4aad8cd1d",
    "log-cli-tools.py": "755492e6e3001182441e58e6ccf0a52fc5f1ccbac8630c6109e114bebb8883af",
    "pm-write-guard.py": "cc9dbea3f5fbfc6d0bb0977a2278b2ea4581acdb86cc2369655762dd363f8ea5",
    "post-bash-dispatcher.py": "dd0239c280bfc3f7e84257d881ff8322f6bc1ec00b8313943bf058f35b1dabeb",
    "secret-scan.py": "e5994787af94620bd14c7b4b5ba5013a67caef5061dc1e9a2faf38c1fb3e43d8",
}


def invoke_hook(
    script_name: str, payload: dict[str, Any], project_dir: Path
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["CLAUDE_PROJECT_DIR"] = str(project_dir)
    environment.pop("CLAUDE_ALLOW_SECRET_WRITE", None)
    return subprocess.run(
        [sys.executable, str(HOOKS_SOURCE / script_name)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        cwd=project_dir,
        env=environment,
    )


def test_canonical_hook_bytes_are_unchanged() -> None:
    actual = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HOOKS_SOURCE.glob("*.py")
    }

    assert actual == EXPECTED_HOOK_SHA256


@pytest.mark.parametrize(
    "script_name,payload",
    [
        (
            "pm-write-guard.py",
            {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": ".claude/tasks/test/brief.md",
                    "content": "ok",
                },
            },
        ),
        (
            "secret-scan.py",
            {
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": ".claude/tasks/test/brief.md",
                    "new_string": "No credential value",
                },
            },
        ),
        (
            "deploy-gate.py",
            {"tool_name": "Bash", "tool_input": {"command": "pytest -q"}},
        ),
        (
            "post-bash-dispatcher.py",
            {
                "tool_name": "Bash",
                "tool_input": {"command": "echo ok"},
                "tool_response": {"stdout": "ok", "stderr": "", "exit_code": 0},
            },
        ),
    ],
)
def test_claude_shaped_allow_behavior_is_unchanged(
    script_name: str, payload: dict[str, Any], tmp_path: Path
) -> None:
    result = invoke_hook(script_name, payload, tmp_path)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_error_to_codex_claude_shape_is_unchanged(tmp_path: Path) -> None:
    result = invoke_hook(
        "error-to-codex.py",
        {
            "tool_name": "Bash",
            "tool_input": {"command": "pytest -q"},
            "tool_response": {
                "stdout": "test_example FAILED with AssertionError",
                "stderr": "",
                "exit_code": 1,
            },
        },
        tmp_path,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "ERROR DETECTED" in context
    assert "Recommended flow" in context


def test_log_cli_tools_claude_shape_is_unchanged(tmp_path: Path) -> None:
    result = invoke_hook(
        "log-cli-tools.py",
        {
            "session_id": "characterization-session",
            "tool_name": "Bash",
            "tool_input": {"command": "codex status"},
            "tool_response": {"stdout": "ok", "stderr": "", "exit_code": 0},
        },
        tmp_path,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    entries = (
        (tmp_path / ".claude" / "logs" / "cli-tools.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    assert len(entries) == 1
    entry = json.loads(entries[0])
    assert entry["tool"] == "codex"
    assert entry["mode"] == "status"
    assert entry["exit_code"] == 0
