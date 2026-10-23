"""Tests for the single local CI entry point (scripts/ci.py).

Two seams are exercised:
- the CLI surface, via subprocess, for behaviour that needs no real tool
  invocation (``--list``, unknown stage names);
- the ``run_stages`` orchestration function, imported directly and given a
  small fake registry of trivial commands, so stage selection, stop-on-first
  -failure and ``--keep-going`` aggregation are proven without re-testing
  ruff/pytest/bandit themselves.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CI_SCRIPT = ROOT / "scripts" / "ci.py"

from scripts import ci


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CI_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_list_prints_every_registered_stage_name():
    result = run_cli("--list")
    assert result.returncode == 0
    for stage in ci.STAGES:
        assert stage.name in result.stdout


def test_registered_stages_cover_the_agreed_checks():
    # Independent source of truth: the stage names the spec agreed on
    # (issue #41), not a value derived from the implementation itself.
    expected = {
        "lint",
        "format",
        "hygiene",
        "django",
        "lockfile",
        "test",
        "security",
        "audit",
        "secrets",
    }
    assert expected <= {stage.name for stage in ci.STAGES}


def test_unknown_stage_name_fails_with_a_clear_message():
    result = run_cli("not-a-real-stage")
    assert result.returncode != 0
    assert "not-a-real-stage" in result.stderr


def _fake_stage(name, marker_dir, *, succeeds):
    marker = marker_dir / name
    code = (
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran'); "
        f"raise SystemExit({0 if succeeds else 1})"
    )
    return ci.Stage(
        name=name,
        description=f"fake stage that {'succeeds' if succeeds else 'fails'}",
        commands=ci.static((sys.executable, "-c", code)),
    )


def test_run_stages_stops_at_the_first_failure_by_default(tmp_path):
    registry = (
        _fake_stage("ok", tmp_path, succeeds=True),
        _fake_stage("broken", tmp_path, succeeds=False),
        _fake_stage("never-runs", tmp_path, succeeds=True),
    )

    exit_code = ci.run_stages(registry, [])

    assert exit_code == 1
    assert (tmp_path / "ok").exists()
    assert (tmp_path / "broken").exists()
    assert not (tmp_path / "never-runs").exists()


def test_keep_going_runs_every_requested_stage_and_reports_failure(tmp_path):
    registry = (
        _fake_stage("ok", tmp_path, succeeds=True),
        _fake_stage("broken", tmp_path, succeeds=False),
        _fake_stage("also-ok", tmp_path, succeeds=True),
    )

    exit_code = ci.run_stages(registry, [], keep_going=True)

    assert exit_code != 0
    assert (tmp_path / "ok").exists()
    assert (tmp_path / "broken").exists()
    assert (tmp_path / "also-ok").exists()


def test_run_stages_runs_only_the_requested_stage(tmp_path):
    registry = (
        _fake_stage("ok", tmp_path, succeeds=True),
        _fake_stage("broken", tmp_path, succeeds=False),
    )

    exit_code = ci.run_stages(registry, ["ok"])

    assert exit_code == 0
    assert (tmp_path / "ok").exists()
    assert not (tmp_path / "broken").exists()
