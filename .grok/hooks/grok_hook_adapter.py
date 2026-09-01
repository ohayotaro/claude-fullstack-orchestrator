#!/usr/bin/env python3
"""Normalize Grok Build hooks and delegate to canonical Claude hooks.

PreToolUse failures are converted to an explicit deny. Failures are advisory
only for a consistently identified PostToolUse advisory route.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ENFORCEMENT_EVENT = "PreToolUse"
ADVISORY_EVENT = "PostToolUse"
WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})
TOOL_ALIASES = {
    "Write": "Write",
    "write": "Write",
    "write_file": "Write",
    "Edit": "Edit",
    "edit": "Edit",
    "edit_file": "Edit",
    "MultiEdit": "MultiEdit",
    "multi_edit": "MultiEdit",
    "NotebookEdit": "NotebookEdit",
    "notebook_edit": "NotebookEdit",
    "Bash": "Bash",
    "bash": "Bash",
    "shell": "Bash",
}
HANDLERS = {
    "secret-scan": (ENFORCEMENT_EVENT, WRITE_TOOLS, "secret-scan.py"),
    "pm-write-guard": (ENFORCEMENT_EVENT, WRITE_TOOLS, "pm-write-guard.py"),
    "deploy-gate": (ENFORCEMENT_EVENT, frozenset({"Bash"}), "deploy-gate.py"),
    "post-bash-dispatcher": (
        ADVISORY_EVENT,
        frozenset({"Bash"}),
        "post-bash-dispatcher.py",
    ),
}
DEFAULT_TIMEOUT_SECONDS = {
    ENFORCEMENT_EVENT: 4.0,
    ADVISORY_EVENT: 9.0,
}
_MISSING = object()


class AdapterError(Exception):
    """A validation or delegation failure at the hook boundary."""


class AdapterArgumentParser(argparse.ArgumentParser):
    """Raise validation errors instead of terminating without denial JSON."""

    def error(self, message: str) -> None:
        raise AdapterError(f"invalid adapter arguments: {message}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AdapterError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> Any:
    raise AdapterError(f"non-standard JSON constant is not allowed: {value}")


def parse_payload(raw: str) -> dict[str, Any]:
    """Parse a hook payload as strict JSON with duplicate-key rejection."""

    if not raw.strip():
        raise AdapterError("hook payload is empty")
    try:
        payload = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_constant,
        )
    except AdapterError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise AdapterError(f"hook payload is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AdapterError("hook payload must be a JSON object")
    return payload


def _alias_value(
    payload: dict[str, Any],
    camel_name: str,
    snake_name: str,
    *,
    default: Any = _MISSING,
) -> Any:
    camel_value = payload.get(camel_name, _MISSING)
    snake_value = payload.get(snake_name, _MISSING)
    if (
        camel_value is not _MISSING
        and snake_value is not _MISSING
        and camel_value != snake_value
    ):
        raise AdapterError(
            f"conflicting payload aliases: {camel_name} and {snake_name}"
        )
    if camel_value is not _MISSING:
        return camel_value
    if snake_value is not _MISSING:
        return snake_value
    return default


def _normalize_tool_name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdapterError("tool name is missing or is not a non-empty string")
    normalized = TOOL_ALIASES.get(value)
    if normalized is None:
        raise AdapterError(f"unsupported tool name: {value}")
    return normalized


def normalize_payload(
    payload: dict[str, Any], expected_event: str, environment: dict[str, str]
) -> tuple[dict[str, Any], str | None]:
    """Return a Claude-shaped payload and the asserted workspace root."""

    payload_event = _alias_value(
        payload, "hookEventName", "hook_event_name", default=None
    )
    environment_event = environment.get("GROK_HOOK_EVENT")
    for source, value in (
        ("payload", payload_event),
        ("GROK_HOOK_EVENT", environment_event),
    ):
        if value is not None and value != expected_event:
            raise AdapterError(
                f"{source} event {value!r} does not match expected {expected_event!r}"
            )

    raw_tool_name = _alias_value(payload, "toolName", "tool_name")
    if raw_tool_name is _MISSING:
        raise AdapterError("unknown payload shape: toolName/tool_name is missing")
    tool_name = _normalize_tool_name(raw_tool_name)

    tool_input = _alias_value(payload, "toolInput", "tool_input")
    if tool_input is _MISSING:
        raise AdapterError("unknown payload shape: toolInput/tool_input is missing")
    if not isinstance(tool_input, dict):
        raise AdapterError("tool input must be a JSON object")

    payload_root = _alias_value(
        payload, "workspaceRoot", "workspace_root", default=None
    )
    environment_root = environment.get("GROK_WORKSPACE_ROOT")
    if payload_root is not None and not isinstance(payload_root, str):
        raise AdapterError("workspace root must be a string when supplied")
    if payload_root and environment_root:
        if Path(payload_root).resolve() != Path(environment_root).resolve():
            raise AdapterError(
                "payload workspaceRoot conflicts with GROK_WORKSPACE_ROOT"
            )
    asserted_root = payload_root or environment_root

    normalized: dict[str, Any] = {
        "hook_event_name": expected_event,
        "tool_name": tool_name,
        "tool_input": tool_input,
    }
    session_id = _alias_value(payload, "sessionId", "session_id", default=None)
    if session_id is not None:
        normalized["session_id"] = session_id
    if "cwd" in payload:
        normalized["cwd"] = payload["cwd"]
    if asserted_root:
        normalized["workspace_root"] = asserted_root

    tool_response = _alias_value(
        payload, "toolResponse", "tool_response", default=_MISSING
    )
    tool_result = _alias_value(payload, "toolResult", "tool_result", default=_MISSING)
    if tool_response is not _MISSING and tool_result is not _MISSING:
        if tool_response != tool_result:
            raise AdapterError("conflicting payload result fields")
    if tool_response is not _MISSING:
        normalized["tool_response"] = tool_response
    elif tool_result is not _MISSING:
        normalized["tool_response"] = tool_result

    tool_output = _alias_value(payload, "toolOutput", "tool_output", default=_MISSING)
    if tool_output is not _MISSING:
        normalized["tool_output"] = tool_output
    return normalized, asserted_root


def repository_root() -> Path:
    """Derive the authoritative checkout root from this adapter's path."""

    return Path(__file__).resolve().parents[2]


def validate_workspace(asserted_root: str | None, repo_root: Path) -> None:
    """Reject a payload/environment identity that names another checkout."""

    if asserted_root is None:
        return
    try:
        candidate = Path(asserted_root).resolve(strict=True)
        authoritative = repo_root.resolve(strict=True)
    except OSError as exc:
        raise AdapterError(f"workspace root cannot be resolved: {exc}") from exc
    if candidate != authoritative:
        raise AdapterError(
            f"workspace root {candidate} does not match adapter root {authoritative}"
        )


def validate_route(handler: str, expected_event: str, tool_name: str) -> str:
    """Validate registration identity and return the canonical script name."""

    route = HANDLERS.get(handler)
    if route is None:
        raise AdapterError(f"handler is not allowlisted: {handler}")
    route_event, allowed_tools, script_name = route
    if route_event != expected_event:
        raise AdapterError(
            f"handler {handler} is not registered for event {expected_event}"
        )
    if tool_name not in allowed_tools:
        raise AdapterError(
            f"handler {handler} cannot process normalized tool {tool_name}"
        )
    return script_name


def validate_enforcement_input(
    expected_event: str, tool_name: str, tool_input: dict[str, Any]
) -> None:
    """Require inspectable target and content fields for enforcement tools."""

    if expected_event != ENFORCEMENT_EVENT:
        return
    if tool_name == "Bash":
        field_name = "command"
    elif tool_name == "NotebookEdit":
        field_name = "notebook_path"
    elif tool_name in WRITE_TOOLS:
        field_name = "file_path"
    else:
        raise AdapterError(f"unsupported enforcement tool: {tool_name}")

    value = tool_input.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise AdapterError(
            f"{tool_name} {field_name} must be a non-empty, non-whitespace string"
        )

    if tool_name == "Write":
        if not isinstance(tool_input.get("content"), str):
            raise AdapterError("Write content must be a string")
    elif tool_name == "Edit":
        if not isinstance(tool_input.get("new_string"), str):
            raise AdapterError("Edit new_string must be a string")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits")
        if not isinstance(edits, list) or not edits:
            raise AdapterError("MultiEdit edits must be a non-empty list")
        for index, edit in enumerate(edits):
            if not isinstance(edit, dict) or not isinstance(
                edit.get("new_string"), str
            ):
                raise AdapterError(
                    "MultiEdit edits must contain only objects with string "
                    f"new_string fields (invalid item at index {index})"
                )
    elif tool_name == "NotebookEdit":
        if not isinstance(tool_input.get("new_source"), str):
            raise AdapterError("NotebookEdit new_source must be a string")


def run_handler(
    script_path: Path,
    normalized_payload: dict[str, Any],
    repo_root: Path,
    timeout_seconds: float,
) -> subprocess.CompletedProcess[str]:
    """Run a canonical hook with a bounded timeout and isolated child env."""

    if not script_path.is_file():
        raise AdapterError(f"canonical hook script is missing: {script_path}")
    child_environment = os.environ.copy()
    child_environment["CLAUDE_PROJECT_DIR"] = str(repo_root)
    try:
        return subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(normalized_payload),
            text=True,
            capture_output=True,
            check=False,
            cwd=repo_root,
            env=child_environment,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdapterError(
            f"canonical hook timed out after {timeout_seconds:g} seconds"
        ) from exc
    except OSError as exc:
        raise AdapterError(f"canonical hook could not start: {exc}") from exc


def _emit_child_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        sys.stdout.write(result.stdout)
        sys.stdout.flush()
    if result.stderr:
        sys.stderr.write(result.stderr)
        sys.stderr.flush()


def validate_child_output(result: subprocess.CompletedProcess[str]) -> None:
    """Ensure non-empty stdout cannot make Grok treat the hook as malformed."""

    if not result.stdout.strip():
        return
    try:
        output = json.loads(
            result.stdout,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_constant,
        )
    except (AdapterError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise AdapterError(f"canonical hook emitted malformed JSON: {exc}") from exc
    if not isinstance(output, dict):
        raise AdapterError("canonical hook stdout JSON must be an object")


def deny(reason: str) -> int:
    """Emit both human-readable and machine-readable denial evidence."""

    message = f"Grok hook adapter denied the tool call: {reason}"
    print(message, file=sys.stderr)
    json.dump({"decision": "deny", "reason": message}, sys.stdout)
    sys.stdout.write("\n")
    return 2


def warn(reason: str) -> int:
    print(f"Grok hook adapter advisory warning: {reason}", file=sys.stderr)
    return 0


def _is_consistent_advisory_route(
    handler: str,
    expected_event: str,
    payload: dict[str, Any],
    environment: dict[str, str],
) -> bool:
    """Return whether at least one event signal identifies the advisory route."""

    route = HANDLERS.get(handler)
    if route is None or route[0] != ADVISORY_EVENT:
        return False
    if expected_event != ADVISORY_EVENT:
        return False

    payload_event = _alias_value(
        payload, "hookEventName", "hook_event_name", default=None
    )
    environment_event = environment.get("GROK_HOOK_EVENT")
    event_signals = (payload_event, environment_event)
    return any(event is not None for event in event_signals) and all(
        event is None or event == ADVISORY_EVENT for event in event_signals
    )


def execute(handler: str, expected_event: str, raw_payload: str) -> int:
    """Validate, normalize, delegate, and translate the child result."""

    advisory = False
    try:
        if expected_event not in DEFAULT_TIMEOUT_SECONDS:
            raise AdapterError(f"unsupported expected event: {expected_event}")
        payload = parse_payload(raw_payload)
        environment = dict(os.environ)
        normalized, asserted_root = normalize_payload(
            payload, expected_event, environment
        )
        repo_root = repository_root()
        validate_workspace(asserted_root, repo_root)
        script_name = validate_route(handler, expected_event, normalized["tool_name"])
        validate_enforcement_input(
            expected_event, normalized["tool_name"], normalized["tool_input"]
        )
        advisory = _is_consistent_advisory_route(
            handler, expected_event, payload, environment
        )
        if expected_event == ADVISORY_EVENT and not advisory:
            raise AdapterError(
                "PostToolUse advisory route is not positively identified"
            )
        script_path = repo_root / ".claude" / "hooks" / script_name
        result = run_handler(
            script_path,
            normalized,
            repo_root,
            DEFAULT_TIMEOUT_SECONDS[expected_event],
        )
        if result.returncode not in {0, 2}:
            raise AdapterError(
                f"canonical hook {script_name} returned unexpected exit code "
                f"{result.returncode}"
            )
        validate_child_output(result)
        _emit_child_output(result)
        return result.returncode
    except Exception as exc:  # fail closed at the external safety boundary
        reason = str(exc) or exc.__class__.__name__
        if advisory:
            return warn(reason)
        return deny(reason)


def build_parser() -> argparse.ArgumentParser:
    parser = AdapterArgumentParser(description=__doc__)
    parser.add_argument(
        "--event", required=True, choices=sorted(DEFAULT_TIMEOUT_SECONDS)
    )
    parser.add_argument("--handler", required=True, choices=sorted(HANDLERS))
    return parser


def _argument_values(arguments: list[str], option: str) -> list[str]:
    """Collect explicit option values without trusting malformed arguments."""

    values: list[str] = []
    for index, argument in enumerate(arguments):
        if argument == option and index + 1 < len(arguments):
            values.append(arguments[index + 1])
        elif argument.startswith(f"{option}="):
            values.append(argument.split("=", 1)[1])
    return values


def _arguments_identify_advisory_route(
    arguments: list[str], environment: dict[str, str]
) -> bool:
    """Trust an advisory hint only when all pre-execution signals agree."""

    event_values = _argument_values(arguments, "--event")
    handler_values = _argument_values(arguments, "--handler")
    if event_values != [ADVISORY_EVENT]:
        return False
    if handler_values != ["post-bash-dispatcher"]:
        return False
    environment_event = environment.get("GROK_HOOK_EVENT")
    return environment_event is None or environment_event == ADVISORY_EVENT


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    advisory_hint = _arguments_identify_advisory_route(arguments, dict(os.environ))
    try:
        args = build_parser().parse_args(arguments)
        raw_payload = sys.stdin.read()
    except Exception as exc:  # protect failures before execute() establishes context
        reason = str(exc) or exc.__class__.__name__
        if advisory_hint:
            return warn(reason)
        return deny(reason)
    return execute(args.handler, args.event, raw_payload)


if __name__ == "__main__":
    raise SystemExit(main())
