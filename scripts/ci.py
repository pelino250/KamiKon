#!/usr/bin/env python3
"""Single local entry point for every CI check.

    uv run --locked python scripts/ci.py              # run every stage
    uv run --locked python scripts/ci.py STAGE ...     # run one or more named stages
    uv run python scripts/ci.py --list                 # list stage names and exit

``--locked`` makes uv fail fast if uv.lock is stale instead of silently
rewriting it, which matters most for the "lockfile" stage itself. GitHub
Actions calls this same script, one stage per job, so a developer's green
run locally is the same command the CI job ran.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass

Command = tuple[str, ...]
CommandBuilder = Callable[[], tuple[Command, ...]]


@dataclass(frozen=True)
class Stage:
    name: str
    description: str
    commands: CommandBuilder


def static(*commands: Command) -> CommandBuilder:
    """Wrap fixed commands so every stage is built the same lazy way."""
    return lambda: commands


def _tracked_files() -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return tuple(result.stdout.splitlines())


def _secrets_commands() -> tuple[Command, ...]:
    return (
        ("uv", "run", "detect-secrets-hook", "--baseline", ".secrets.baseline", *_tracked_files()),
    )


STAGES: tuple[Stage, ...] = (
    Stage(
        name="lint",
        description="Ruff static analysis.",
        commands=static(("uv", "run", "ruff", "check", ".")),
    ),
    Stage(
        name="format",
        description="Ruff formatting check (no files rewritten).",
        commands=static(("uv", "run", "ruff", "format", "--check", ".")),
    ),
    Stage(
        name="hygiene",
        description="Fast file hygiene hooks (yaml, EOF, trailing whitespace).",
        commands=static(("uv", "run", "pre-commit", "run", "--all-files")),
    ),
    Stage(
        name="django",
        description="Django system checks and migration drift.",
        commands=static(
            ("uv", "run", "python", "manage.py", "check"),
            ("uv", "run", "python", "manage.py", "makemigrations", "--check", "--dry-run"),
        ),
    ),
    Stage(
        name="lockfile",
        description="uv.lock matches pyproject.toml.",
        commands=static(("uv", "lock", "--check")),
    ),
    Stage(
        name="test",
        description="pytest with a coverage report and minimum threshold.",
        # The threshold itself lives in [tool.coverage.report] in
        # pyproject.toml, the single source of truth for that number.
        commands=static(
            ("uv", "run", "pytest", "--cov=apps", "--cov=kamikon", "--cov-report=term-missing"),
        ),
    ),
    Stage(
        name="security",
        description="bandit static security scan of application code.",
        commands=static(
            ("uv", "run", "bandit", "-c", "pyproject.toml", "-r", "apps", "kamikon", "manage.py")
        ),
    ),
    Stage(
        name="audit",
        description="pip-audit dependency vulnerability scan.",
        commands=static(("uv", "run", "pip-audit")),
    ),
    Stage(
        name="secrets",
        description="detect-secrets scan against the committed baseline.",
        commands=_secrets_commands,
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stages", nargs="*", help="Stage names to run (default: all).")
    parser.add_argument("--list", action="store_true", help="List stage names and exit.")
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Run every requested stage even after one fails.",
    )
    return parser


def resolve_stages(registry: tuple[Stage, ...], names: list[str]) -> tuple[Stage, ...]:
    if not names:
        return registry
    by_name = {stage.name: stage for stage in registry}
    unknown = [name for name in names if name not in by_name]
    if unknown:
        known = ", ".join(sorted(by_name))
        raise SystemExit(f"Unknown stage(s): {', '.join(unknown)}. Known stages: {known}.")
    return tuple(by_name[name] for name in names)


def run_stages(
    registry: tuple[Stage, ...],
    names: list[str],
    *,
    keep_going: bool = False,
) -> int:
    stages = resolve_stages(registry, names)
    exit_code = 0
    for stage in stages:
        for command in stage.commands():
            print(f"-- {stage.name}: {' '.join(command)}")
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                print(
                    f"-- {stage.name} failed. Reproduce with: {' '.join(command)}",
                    file=sys.stderr,
                )
                exit_code = result.returncode
                if not keep_going:
                    return exit_code
                break
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        for stage in STAGES:
            print(f"{stage.name}\t{stage.description}")
        return 0

    try:
        return run_stages(STAGES, args.stages, keep_going=args.keep_going)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
