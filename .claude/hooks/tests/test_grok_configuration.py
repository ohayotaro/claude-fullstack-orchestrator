from __future__ import annotations

import json
import re
import tomllib

import pytest

from conftest import REPO_ROOT


GROK_ROOT = REPO_ROOT / ".grok"
ALLOWED_COMMANDS = [
    "git status --short",
    "git diff --stat",
    "git log -1",
    "python3 -m pytest",
    "codex status",
    "mkdir -p tmp",
    "ls -la",
    "pnpm test",
    "pnpm lint",
    "npm test",
    "npm run lint",
    "pytest -q",
    "ruff check .",
    "mypy src",
    "uv run pytest",
    "swiftlint lint",
    "ktlint src",
    "dart test",
    "flutter test",
    "playwright test",
]
FORBIDDEN_COMMANDS = {
    "deny-recursive-force-delete": "rm -rf build",
    "deny-hook-bypass": "git commit --no-verify",
    "deny-codex-network-search": "codex --search topic",
    "deny-codex-sandbox-bypass": (
        "codex --dangerously-bypass-approvals-and-sandbox exec"
    ),
}
FORBIDDEN_TOKENS = {
    "deny-recursive-force-delete": "rm -rf",
    "deny-hook-bypass": "git commit --no-verify",
    "deny-codex-network-search": "codex --search",
    "deny-codex-sandbox-bypass": ("codex --dangerously-bypass-approvals-and-sandbox"),
}


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def load_permission_patterns() -> tuple[
    dict[str, re.Pattern[str]], list[re.Pattern[str]]
]:
    with (GROK_ROOT / "config.toml").open("rb") as config_file:
        config = tomllib.load(config_file)
    rules = config["permissions"]["rules"]
    deny_patterns = {
        rule["name"]: re.compile(rule["pattern"])
        for rule in rules
        if rule["action"] == "deny"
    }
    allow_patterns = [
        re.compile(rule["pattern"]) for rule in rules if rule["action"] == "allow"
    ]
    return deny_patterns, allow_patterns


def test_config_is_valid_and_required_denies_match() -> None:
    with (GROK_ROOT / "config.toml").open("rb") as config_file:
        config = tomllib.load(config_file)
    deny_patterns, _ = load_permission_patterns()

    assert config["permissions"]["default"] == "ask"
    assert config["permissions"]["deny_precedence"] is True
    assert deny_patterns["deny-recursive-force-delete"].search("rm -rf build")
    assert deny_patterns["deny-hook-bypass"].search("git commit --no-verify")
    assert deny_patterns["deny-codex-network-search"].search(
        "codex exec --search topic"
    )
    assert deny_patterns["deny-codex-sandbox-bypass"].search(
        "codex --dangerously-bypass-approvals-and-sandbox exec"
    )


@pytest.mark.parametrize(
    ("deny_rule", "command", "matches_allow"),
    [
        ("deny-hook-bypass", "git commit --no-verify", False),
        ("deny-hook-bypass", "git commit --no-verify; true", False),
        ("deny-hook-bypass", "git commit --no-verify&& true", False),
        ("deny-hook-bypass", "git commit --no-verify& true", False),
        ("deny-hook-bypass", "git commit --no-verify| true", False),
        ("deny-hook-bypass", "git commit --no-verify|| true", False),
        ("deny-codex-network-search", "codex --search", True),
        ("deny-codex-network-search", "codex --search; true", True),
        ("deny-codex-network-search", "codex --search&& true", True),
        ("deny-codex-network-search", "codex --search& true", True),
        ("deny-codex-network-search", "codex --search| true", True),
        ("deny-codex-network-search", "codex --search|| true", True),
        (
            "deny-codex-sandbox-bypass",
            "codex --dangerously-bypass-approvals-and-sandbox",
            True,
        ),
        (
            "deny-codex-sandbox-bypass",
            "codex --dangerously-bypass-approvals-and-sandbox; true",
            True,
        ),
        (
            "deny-codex-sandbox-bypass",
            "codex --dangerously-bypass-approvals-and-sandbox&& true",
            True,
        ),
        (
            "deny-codex-sandbox-bypass",
            "codex --dangerously-bypass-approvals-and-sandbox& true",
            True,
        ),
        (
            "deny-codex-sandbox-bypass",
            "codex --dangerously-bypass-approvals-and-sandbox| true",
            True,
        ),
        (
            "deny-codex-sandbox-bypass",
            "codex --dangerously-bypass-approvals-and-sandbox|| true",
            True,
        ),
    ],
)
def test_forbidden_flags_match_with_shell_separator_boundaries(
    deny_rule: str,
    command: str,
    matches_allow: bool,
) -> None:
    deny_patterns, allow_patterns = load_permission_patterns()

    assert deny_patterns[deny_rule].search(command), command
    assert any(pattern.search(command) for pattern in deny_patterns.values()), command
    assert any(pattern.search(command) for pattern in allow_patterns) is matches_allow


def test_config_preserves_every_allowed_command_family() -> None:
    _, allow_patterns = load_permission_patterns()

    for command in ALLOWED_COMMANDS:
        assert any(pattern.search(command) for pattern in allow_patterns), command


@pytest.mark.parametrize("trailing_newline", [False, True])
def test_multiline_forbidden_commands_override_every_allow_family(
    trailing_newline: bool,
) -> None:
    deny_patterns, allow_patterns = load_permission_patterns()

    for allowed_command in ALLOWED_COMMANDS:
        for deny_rule, forbidden_command in FORBIDDEN_COMMANDS.items():
            command = f"{allowed_command}\n{forbidden_command}"
            if trailing_newline:
                command += "\n"

            assert any(pattern.search(command) for pattern in allow_patterns), command
            assert deny_patterns[deny_rule].search(command), command
            assert any(pattern.search(command) for pattern in deny_patterns.values()), (
                command
            )


@pytest.mark.parametrize(
    "suffix",
    ["$(printf '')", chr(96) + "printf ''" + chr(96)],
    ids=["dollar-paren", "backtick"],
)
def test_forbidden_commands_match_command_substitution_boundaries(
    suffix: str,
) -> None:
    deny_patterns, _ = load_permission_patterns()

    for deny_rule, forbidden_command in FORBIDDEN_TOKENS.items():
        command = f"{forbidden_command}{suffix} operand"
        assert deny_patterns[deny_rule].search(command), command


@pytest.mark.parametrize(
    ("deny_rule", "command", "matches_allow"),
    [
        ("deny-recursive-force-delete", "ls $(rm -rf build)", True),
        ("deny-recursive-force-delete", "ls $( rm -rf build)", True),
        ("deny-recursive-force-delete", "ls `rm -rf build`", True),
        ("deny-recursive-force-delete", "ls ` rm -rf build`", True),
        ("deny-hook-bypass", "ls $(--no-verify)", True),
        ("deny-hook-bypass", "ls `--no-verify`", True),
        ("deny-codex-network-search", "echo $(codex --search)", False),
        ("deny-codex-network-search", "ls $(codex --search)", True),
        (
            "deny-codex-sandbox-bypass",
            "ls `codex --dangerously-bypass-approvals-and-sandbox`",
            True,
        ),
    ],
)
def test_forbidden_commands_match_inside_command_substitutions(
    deny_rule: str,
    command: str,
    matches_allow: bool,
) -> None:
    deny_patterns, allow_patterns = load_permission_patterns()

    assert deny_patterns[deny_rule].search(command), command
    assert any(pattern.search(command) for pattern in deny_patterns.values()), command
    assert any(pattern.search(command) for pattern in allow_patterns) is matches_allow


def test_hook_registration_is_strict_and_targets_adapter() -> None:
    registration_path = GROK_ROOT / "hooks" / "hooks.json"
    registration = json.loads(
        registration_path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
    )
    commands: list[str] = []
    for event_groups in registration["hooks"].values():
        for group in event_groups:
            for hook in group["hooks"]:
                assert hook["type"] == "command"
                commands.append(hook["command"])

    assert len(commands) == 4
    assert len(set(commands)) == 4
    assert all(".grok/hooks/grok_hook_adapter.py" in command for command in commands)
    assert any(
        "--event PreToolUse --handler secret-scan" in command for command in commands
    )
    assert any(
        "--event PreToolUse --handler pm-write-guard" in command for command in commands
    )
    assert any(
        "--event PreToolUse --handler deploy-gate" in command for command in commands
    )
    assert any(
        "--event PostToolUse --handler post-bash-dispatcher" in command
        for command in commands
    )


def test_adapter_tree_and_shared_skills_link() -> None:
    required_files = [
        GROK_ROOT / "config.toml",
        GROK_ROOT / "README.md",
        GROK_ROOT / "rules" / "00-pm-identity.md",
        GROK_ROOT / "rules" / "10-harness-mapping.md",
        GROK_ROOT / "hooks" / "hooks.json",
        GROK_ROOT / "hooks" / "grok_hook_adapter.py",
    ]

    assert all(path.is_file() for path in required_files)
    assert (GROK_ROOT / "skills").is_symlink()
    assert (GROK_ROOT / "skills").resolve() == (
        REPO_ROOT / ".claude" / "skills"
    ).resolve()
