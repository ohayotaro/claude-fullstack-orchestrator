from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


ENFORCEMENT_ROUTES = (
    (
        "pm-write-guard",
        "Write",
        {
            "file_path": ".claude/tasks/example/brief.md",
            "content": "Harmless task content",
        },
    ),
    (
        "secret-scan",
        "Write",
        {
            "file_path": ".claude/tasks/example/brief.md",
            "content": "Harmless task content",
        },
    ),
    ("deploy-gate", "Bash", {"command": "pytest -q"}),
)


def grok_write_payload(repo_root: Path, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "hookEventName": "PreToolUse",
        "toolName": "Write",
        "toolInput": {
            "file_path": ".claude/tasks/example/brief.md",
            "content": "Harmless task content",
        },
        "workspaceRoot": str(repo_root),
    }
    payload.update(overrides)
    return payload


def assert_internal_denial(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 2
    output = json.loads(result.stdout)
    assert output["decision"] == "deny"
    assert output["reason"]
    assert "denied" in result.stderr


def test_normalizes_grok_camel_case_payload(
    adapter_module: ModuleType, tmp_path: Path
) -> None:
    payload = {
        "hookEventName": "PreToolUse",
        "sessionId": "session-1",
        "cwd": str(tmp_path),
        "workspaceRoot": str(tmp_path),
        "toolName": "write_file",
        "toolInput": {"file_path": "README.md", "content": "ok"},
    }

    normalized, asserted_root = adapter_module.normalize_payload(
        payload, "PreToolUse", {}
    )

    assert normalized == {
        "hook_event_name": "PreToolUse",
        "session_id": "session-1",
        "cwd": str(tmp_path),
        "workspace_root": str(tmp_path),
        "tool_name": "Write",
        "tool_input": {"file_path": "README.md", "content": "ok"},
    }
    assert asserted_root == str(tmp_path)


def test_normalizes_claude_snake_case_payload(adapter_module: ModuleType) -> None:
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "pytest -q"},
        "tool_response": {"stdout": "passed", "stderr": "", "exit_code": 0},
    }

    normalized, asserted_root = adapter_module.normalize_payload(
        payload, "PostToolUse", {}
    )

    assert normalized["hook_event_name"] == "PostToolUse"
    assert normalized["tool_name"] == "Bash"
    assert normalized["tool_input"] == {"command": "pytest -q"}
    assert normalized["tool_response"]["exit_code"] == 0
    assert asserted_root is None


def test_normalizes_grok_post_tool_result(adapter_module: ModuleType) -> None:
    payload = {
        "hookEventName": "PostToolUse",
        "toolName": "bash",
        "toolInput": {"command": "pytest -q"},
        "toolResult": {"stdout": "passed", "stderr": "", "exit_code": 0},
    }

    normalized, _ = adapter_module.normalize_payload(payload, "PostToolUse", {})

    assert normalized["tool_name"] == "Bash"
    assert normalized["tool_response"]["stdout"] == "passed"


def test_allows_pm_artifact_write(run_adapter: Any, isolated_repo: Path) -> None:
    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload=grok_write_payload(isolated_repo),
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_preserves_source_write_denial(run_adapter: Any, isolated_repo: Path) -> None:
    payload = grok_write_payload(isolated_repo)
    payload["toolInput"] = {"file_path": "services/api.py", "content": "pass"}

    result = run_adapter(handler="pm-write-guard", event="PreToolUse", payload=payload)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "source/config writes are blocked" in result.stderr


def test_pm_write_guard_blocks_grok_configuration(
    run_adapter: Any, isolated_repo: Path
) -> None:
    payload = grok_write_payload(isolated_repo)
    payload["toolInput"] = {
        "file_path": ".grok/config.toml",
        "content": "default = 'allow'",
    }

    result = run_adapter(handler="pm-write-guard", event="PreToolUse", payload=payload)

    assert result.returncode == 2
    assert "source/config writes are blocked" in result.stderr


def test_preserves_deploy_gate_denial(run_adapter: Any, isolated_repo: Path) -> None:
    result = run_adapter(
        handler="deploy-gate",
        event="PreToolUse",
        payload={
            "hookEventName": "PreToolUse",
            "toolName": "Bash",
            "toolInput": {"command": "vercel --prod"},
            "workspaceRoot": str(isolated_repo),
        },
    )

    assert result.returncode == 2
    assert "without valid acknowledgment" in result.stderr


@pytest.mark.parametrize(
    "tool_input",
    [
        {},
        {"command": ""},
        {"command": " \t\n"},
        {"command": None},
        {"command": 0},
        {"command": []},
        {"command": {}},
    ],
)
def test_malformed_bash_command_fails_closed_on_deploy_gate_route(
    run_adapter: Any,
    isolated_repo: Path,
    tool_input: dict[str, Any],
) -> None:
    result = run_adapter(
        handler="deploy-gate",
        event="PreToolUse",
        payload={
            "hookEventName": "PreToolUse",
            "toolName": "Bash",
            "toolInput": tool_input,
            "workspaceRoot": str(isolated_repo),
        },
    )

    assert_internal_denial(result)
    assert "Bash command must be a non-empty, non-whitespace string" in result.stdout


@pytest.mark.parametrize(
    "tool_input",
    [
        {},
        {"file_path": ""},
        {"file_path": " \t\n"},
        {"file_path": None},
        {"file_path": 0},
        {"file_path": []},
        {"file_path": {}},
    ],
)
def test_malformed_write_path_fails_closed_on_secret_scan_route(
    run_adapter: Any,
    isolated_repo: Path,
    tool_input: dict[str, Any],
) -> None:
    result = run_adapter(
        handler="secret-scan",
        event="PreToolUse",
        payload={
            "hookEventName": "PreToolUse",
            "toolName": "Write",
            "toolInput": tool_input,
            "workspaceRoot": str(isolated_repo),
        },
    )

    assert_internal_denial(result)
    assert "Write file_path must be a non-empty" in result.stdout


@pytest.mark.parametrize(
    ("tool_name", "tool_input", "reason_fragment"),
    [
        (
            "Write",
            {"file_path": ".claude/tasks/example/brief.md"},
            "Write content must be a string",
        ),
        (
            "Edit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "new_string": 0,
            },
            "Edit new_string must be a string",
        ),
        (
            "MultiEdit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "edits": {},
            },
            "MultiEdit edits must be a non-empty list",
        ),
        (
            "NotebookEdit",
            {
                "notebook_path": ".claude/tasks/example/notebook.ipynb",
                "new_source": ["source"],
            },
            "NotebookEdit new_source must be a string",
        ),
        (
            "MultiEdit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "edits": [],
            },
            "MultiEdit edits must be a non-empty list",
        ),
        (
            "MultiEdit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "edits": ["replacement"],
            },
            "MultiEdit edits must contain only objects",
        ),
        (
            "MultiEdit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "edits": [{}],
            },
            "MultiEdit edits must contain only objects",
        ),
    ],
)
def test_uninspectable_write_content_fails_closed_on_secret_scan_route(
    run_adapter: Any,
    isolated_repo: Path,
    tool_name: str,
    tool_input: dict[str, Any],
    reason_fragment: str,
) -> None:
    result = run_adapter(
        handler="secret-scan",
        event="PreToolUse",
        payload={
            "hookEventName": "PreToolUse",
            "toolName": tool_name,
            "toolInput": tool_input,
            "workspaceRoot": str(isolated_repo),
        },
    )

    assert_internal_denial(result)
    assert reason_fragment in result.stdout


@pytest.mark.parametrize(
    ("tool_name", "tool_input"),
    [
        (
            "Write",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "content": "",
            },
        ),
        (
            "Edit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "new_string": "",
            },
        ),
        (
            "MultiEdit",
            {
                "file_path": ".claude/tasks/example/brief.md",
                "edits": [{"new_string": ""}],
            },
        ),
        (
            "NotebookEdit",
            {
                "notebook_path": ".claude/tasks/example/notebook.ipynb",
                "new_source": "",
            },
        ),
    ],
)
def test_empty_write_content_remains_valid_on_secret_scan_route(
    run_adapter: Any,
    isolated_repo: Path,
    tool_name: str,
    tool_input: dict[str, Any],
) -> None:
    result = run_adapter(
        handler="secret-scan",
        event="PreToolUse",
        payload={
            "hookEventName": "PreToolUse",
            "toolName": tool_name,
            "toolInput": tool_input,
            "workspaceRoot": str(isolated_repo),
        },
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize("notebook_path", [None, "", " \t\n", 0, [], {}])
def test_malformed_notebook_path_fails_closed(
    run_adapter: Any,
    isolated_repo: Path,
    notebook_path: Any,
) -> None:
    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload={
            "tool_name": "NotebookEdit",
            "tool_input": {"notebook_path": notebook_path},
            "workspace_root": str(isolated_repo),
        },
    )

    assert_internal_denial(result)
    assert "NotebookEdit notebook_path must be a non-empty" in result.stdout


def test_preserves_secret_scan_denial(run_adapter: Any, isolated_repo: Path) -> None:
    fake_secret = "sk-" + ("A" * 32)
    payload = grok_write_payload(isolated_repo)
    payload["toolInput"] = {
        "file_path": ".claude/tasks/example/brief.md",
        "content": f"credential={fake_secret}",
    }

    result = run_adapter(handler="secret-scan", event="PreToolUse", payload=payload)

    assert result.returncode == 2
    assert "probable secret" in result.stderr


@pytest.mark.parametrize(
    "raw_payload, reason_fragment",
    [
        ("not-json", "not valid JSON"),
        ("{}", "unknown payload shape"),
        (
            '{"tool_name":"Write","tool_name":"Edit","tool_input":{}}',
            "duplicate JSON key",
        ),
    ],
)
def test_malformed_enforcement_payloads_fail_closed(
    run_adapter: Any, raw_payload: str, reason_fragment: str
) -> None:
    result = run_adapter(
        handler="pm-write-guard", event="PreToolUse", payload=raw_payload
    )

    assert_internal_denial(result)
    assert reason_fragment in result.stdout


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_json_constants_fail_closed(
    run_adapter: Any, constant: str
) -> None:
    raw_payload = (
        '{"toolName":"Write","toolInput":'
        f'{{"file_path":"README.md","value":{constant}}}}}'
    )

    result = run_adapter(
        handler="pm-write-guard", event="PreToolUse", payload=raw_payload
    )

    assert_internal_denial(result)
    assert f"non-standard JSON constant is not allowed: {constant}" in result.stdout


def test_malformed_post_tool_payload_fails_closed(run_adapter: Any) -> None:
    result = run_adapter(
        handler="post-bash-dispatcher",
        event="PostToolUse",
        payload="not-json",
    )

    assert_internal_denial(result)
    assert "hook payload is not valid JSON" in result.stdout


def test_valid_json_unknown_shape_post_tool_payload_fails_closed(
    run_adapter: Any,
) -> None:
    result = run_adapter(
        handler="post-bash-dispatcher",
        event="PostToolUse",
        payload={},
    )

    assert_internal_denial(result)
    assert "unknown payload shape" in result.stdout


def test_post_tool_payload_without_event_identity_fails_closed(
    run_adapter: Any,
) -> None:
    result = run_adapter(
        handler="post-bash-dispatcher",
        event="PostToolUse",
        payload={
            "tool_name": "Bash",
            "tool_input": {"command": "pytest -q"},
        },
    )

    assert_internal_denial(result)
    assert "advisory route is not positively identified" in result.stdout


def test_conflicting_aliases_fail_closed(run_adapter: Any) -> None:
    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload={
            "toolName": "Write",
            "tool_name": "Edit",
            "toolInput": {},
            "tool_input": {},
        },
    )

    assert_internal_denial(result)
    assert "conflicting payload aliases" in result.stdout


@pytest.mark.parametrize(
    "payload",
    [
        {"toolName": "Unknown", "toolInput": {}},
        {"toolName": "Write", "toolInput": []},
        {"hookEventName": "PostToolUse", "toolName": "Write", "toolInput": {}},
        {"hookEventName": "PreToolUse", "toolName": "Bash", "toolInput": {}},
    ],
)
def test_unknown_or_mismatched_routes_fail_closed(
    run_adapter: Any, payload: dict[str, Any]
) -> None:
    result = run_adapter(handler="pm-write-guard", event="PreToolUse", payload=payload)

    assert_internal_denial(result)


@pytest.mark.parametrize(
    ("handler", "tool_name", "tool_input"),
    ENFORCEMENT_ROUTES,
    ids=[route[0] for route in ENFORCEMENT_ROUTES],
)
@pytest.mark.parametrize("payload_event", ["PreToolUse", "PostToolUse"])
def test_enforcement_handler_with_post_cli_event_fails_closed(
    run_adapter: Any,
    handler: str,
    tool_name: str,
    tool_input: dict[str, Any],
    payload_event: str,
) -> None:
    result = run_adapter(
        handler=handler,
        event="PostToolUse",
        payload={
            "hookEventName": payload_event,
            "toolName": tool_name,
            "toolInput": tool_input,
        },
    )

    assert_internal_denial(result)


@pytest.mark.parametrize(
    ("handler", "tool_name", "tool_input"),
    ENFORCEMENT_ROUTES,
    ids=[route[0] for route in ENFORCEMENT_ROUTES],
)
def test_enforcement_handler_with_mismatched_payload_event_fails_closed(
    run_adapter: Any,
    handler: str,
    tool_name: str,
    tool_input: dict[str, Any],
) -> None:
    result = run_adapter(
        handler=handler,
        event="PreToolUse",
        payload={
            "hookEventName": "PostToolUse",
            "toolName": tool_name,
            "toolInput": tool_input,
        },
    )

    assert_internal_denial(result)


@pytest.mark.parametrize(
    ("payload", "extra_environment"),
    [
        (
            {
                "hookEventName": "PreToolUse",
                "toolName": "Bash",
                "toolInput": {"command": "pytest -q"},
            },
            None,
        ),
        (
            {
                "hookEventName": "PostToolUse",
                "toolName": "Bash",
                "toolInput": {"command": "pytest -q"},
            },
            {"GROK_HOOK_EVENT": "PreToolUse"},
        ),
    ],
)
def test_advisory_handler_with_event_identity_mismatch_fails_closed(
    run_adapter: Any,
    payload: dict[str, Any],
    extra_environment: dict[str, str] | None,
) -> None:
    result = run_adapter(
        handler="post-bash-dispatcher",
        event="PostToolUse",
        payload=payload,
        extra_environment=extra_environment,
    )

    assert_internal_denial(result)


def test_workspace_identity_mismatch_fails_closed(
    run_adapter: Any, isolated_repo: Path, tmp_path: Path
) -> None:
    other_root = tmp_path / "other"
    other_root.mkdir()
    payload = grok_write_payload(isolated_repo, workspaceRoot=str(other_root))

    result = run_adapter(handler="pm-write-guard", event="PreToolUse", payload=payload)

    assert_internal_denial(result)
    assert "does not match adapter root" in result.stdout


def test_payload_and_environment_workspace_conflict_fails_closed(
    run_adapter: Any, isolated_repo: Path, tmp_path: Path
) -> None:
    other_root = tmp_path / "other-environment"
    other_root.mkdir()

    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload=grok_write_payload(isolated_repo),
        extra_environment={"GROK_WORKSPACE_ROOT": str(other_root)},
    )

    assert_internal_denial(result)
    assert "conflicts with GROK_WORKSPACE_ROOT" in result.stdout


def test_missing_canonical_script_fails_closed(
    run_adapter: Any, isolated_repo: Path
) -> None:
    (isolated_repo / ".claude" / "hooks" / "pm-write-guard.py").unlink()

    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload=grok_write_payload(isolated_repo),
    )

    assert_internal_denial(result)
    assert "canonical hook script is missing" in result.stdout


def test_unexpected_child_exit_fails_closed(
    run_adapter: Any, isolated_repo: Path
) -> None:
    script = isolated_repo / ".claude" / "hooks" / "pm-write-guard.py"
    script.write_text("raise SystemExit(7)\n", encoding="utf-8")

    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload=grok_write_payload(isolated_repo),
    )

    assert_internal_denial(result)
    assert "unexpected exit code 7" in result.stdout


def test_malformed_child_output_fails_closed(
    run_adapter: Any, isolated_repo: Path
) -> None:
    script = isolated_repo / ".claude" / "hooks" / "pm-write-guard.py"
    script.write_text("print('not-json')\n", encoding="utf-8")

    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload=grok_write_payload(isolated_repo),
    )

    assert_internal_denial(result)
    assert "emitted malformed JSON" in result.stdout


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_constant_in_child_output_fails_closed(
    run_adapter: Any, isolated_repo: Path, constant: str
) -> None:
    script = isolated_repo / ".claude" / "hooks" / "pm-write-guard.py"
    script.write_text(
        f'print(\'{{"hookSpecificOutput":{{"value":{constant}}}}}\')\n',
        encoding="utf-8",
    )

    result = run_adapter(
        handler="pm-write-guard",
        event="PreToolUse",
        payload=grok_write_payload(isolated_repo),
    )

    assert_internal_denial(result)
    assert "canonical hook emitted malformed JSON" in result.stdout
    assert f"non-standard JSON constant is not allowed: {constant}" in result.stdout


def test_child_timeout_is_an_adapter_error(
    adapter_module: ModuleType, tmp_path: Path
) -> None:
    script = tmp_path / "slow_hook.py"
    script.write_text("import time\ntime.sleep(1)\n", encoding="utf-8")

    with pytest.raises(adapter_module.AdapterError, match="timed out"):
        adapter_module.run_handler(script, {}, tmp_path, 0.01)


def test_unexpected_internal_error_fails_closed(
    adapter_module: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    def explode() -> Path:
        raise RuntimeError("unexpected internal failure")

    monkeypatch.setattr(adapter_module, "repository_root", explode)
    payload = json.dumps({"tool_name": "Write", "tool_input": {}})

    return_code = adapter_module.execute("pm-write-guard", "PreToolUse", payload)

    captured = capsys.readouterr()
    assert return_code == 2
    assert json.loads(captured.out)["decision"] == "deny"
    assert "unexpected internal failure" in captured.err


def test_invalid_adapter_arguments_fail_closed(isolated_repo: Path) -> None:
    adapter_path = isolated_repo / ".grok" / "hooks" / "grok_hook_adapter.py"

    result = subprocess.run(
        [
            sys.executable,
            str(adapter_path),
            "--event",
            "PreToolUse",
            "--handler",
            "not-allowlisted",
        ],
        input="{}",
        text=True,
        capture_output=True,
        check=False,
        cwd=isolated_repo,
    )

    assert_internal_denial(result)
    assert "invalid adapter arguments" in result.stdout


@pytest.mark.parametrize("handler", [route[0] for route in ENFORCEMENT_ROUTES])
def test_pre_execution_failure_cannot_downgrade_enforcement_handler(
    isolated_repo: Path, handler: str
) -> None:
    adapter_path = isolated_repo / ".grok" / "hooks" / "grok_hook_adapter.py"

    result = subprocess.run(
        [
            sys.executable,
            str(adapter_path),
            "--event",
            "PostToolUse",
            "--handler",
            handler,
            "--unexpected-argument",
        ],
        input="{}",
        text=True,
        capture_output=True,
        check=False,
        cwd=isolated_repo,
    )

    assert_internal_denial(result)
    assert "invalid adapter arguments" in result.stdout


def test_consistent_advisory_route_remains_advisory_on_argument_failure(
    isolated_repo: Path,
) -> None:
    adapter_path = isolated_repo / ".grok" / "hooks" / "grok_hook_adapter.py"

    result = subprocess.run(
        [
            sys.executable,
            str(adapter_path),
            "--event",
            "PostToolUse",
            "--handler",
            "post-bash-dispatcher",
            "--unexpected-argument",
        ],
        input="{}",
        text=True,
        capture_output=True,
        check=False,
        cwd=isolated_repo,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert "advisory warning" in result.stderr


def test_environment_mismatch_prevents_advisory_argument_hint(
    isolated_repo: Path,
) -> None:
    adapter_path = isolated_repo / ".grok" / "hooks" / "grok_hook_adapter.py"
    environment = os.environ.copy()
    environment["GROK_HOOK_EVENT"] = "PreToolUse"

    result = subprocess.run(
        [
            sys.executable,
            str(adapter_path),
            "--event",
            "PostToolUse",
            "--handler",
            "post-bash-dispatcher",
            "--unexpected-argument",
        ],
        input="{}",
        text=True,
        capture_output=True,
        check=False,
        cwd=isolated_repo,
        env=environment,
    )

    assert_internal_denial(result)
    assert "invalid adapter arguments" in result.stdout


def test_post_tool_failure_is_advisory(run_adapter: Any, isolated_repo: Path) -> None:
    (isolated_repo / ".claude" / "hooks" / "post-bash-dispatcher.py").unlink()

    result = run_adapter(
        handler="post-bash-dispatcher",
        event="PostToolUse",
        payload={
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest -q"},
        },
    )

    assert result.returncode == 0
    assert "advisory warning" in result.stderr


def test_claude_shape_delegates_without_grok_cli(
    run_adapter: Any, isolated_repo: Path
) -> None:
    result = run_adapter(
        handler="deploy-gate",
        event="PreToolUse",
        payload={"tool_name": "Bash", "tool_input": {"command": "pytest -q"}},
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_run_handler_uses_current_python(
    adapter_module: ModuleType, tmp_path: Path
) -> None:
    script = tmp_path / "python_hook.py"
    script.write_text(
        "import json, sys\njson.dump({'python': sys.executable}, sys.stdout)\n",
        encoding="utf-8",
    )

    result = adapter_module.run_handler(script, {}, tmp_path, 1.0)

    assert result.returncode == 0
    assert json.loads(result.stdout)["python"] == sys.executable
