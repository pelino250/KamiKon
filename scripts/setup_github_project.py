#!/usr/bin/env python3
"""
KamiKon — GitHub Agile setup script.

Turns the sprint plan in `scripts/sprint_backlog.json` (derived from
`agile_devops_roadmap.md`) into live GitHub configuration:

  1. labels      Label taxonomy (type:*, comp:*, learning labels)
  2. milestones  One milestone per sprint (Sprint 0 … Sprint 7) with due dates
  3. issues      One issue per user story / DevOps task, labelled + milestoned
  4. project     GitHub Projects (v2) board with custom fields:
                   Status (6 columns), Track, Priority, Story Points, Sprint (iteration)
                 linked to the repo, with every issue added and its fields set

The script is idempotent: re-running it never duplicates anything.
  * Labels and milestones are created or updated in place.
  * Issues are matched by their `[US-x.x]` / `[DO-x.x]` title prefix and are
    skipped if they already exist (use --update-existing to refresh them).
  * Project items that are already on the board keep their field values, so
    re-running never resets the team's progress (unless --update-existing).

Requirements
  * GitHub CLI (`gh`) >= 2.40, authenticated as a user with admin/write access.
  * Token scopes: `repo` and `project`. Grant `project` with:
        gh auth refresh -h github.com -s project
  * Python 3.9+ (standard library only).

Usage
  python3 scripts/setup_github_project.py                       # everything
  python3 scripts/setup_github_project.py --dry-run             # preview only
  python3 scripts/setup_github_project.py --only labels,milestones,issues
  python3 scripts/setup_github_project.py --start-date 2026-10-19
  GH_TOKEN=$(gh auth token --user <account>) python3 scripts/setup_github_project.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

PHASES = ("labels", "milestones", "issues", "project")
DEFAULT_REPO = "pelino250/KamiKon"
DEFAULT_DATA = Path(__file__).with_name("sprint_backlog.json")

# GitHub's default labels, removed only when --prune-default-labels is passed.
# "good first issue" and "wontfix" are kept: GitHub surfaces the first to new
# contributors, and CONTRIBUTING.md lists the second as a triage label.
GITHUB_DEFAULT_LABELS = (
    "bug",
    "documentation",
    "duplicate",
    "enhancement",
    "help wanted",
    "invalid",
    "question",
)


# --------------------------------------------------------------------------- #
# Small utilities
# --------------------------------------------------------------------------- #
class GhError(RuntimeError):
    pass


def log(msg: str = "") -> None:
    print(msg, flush=True)


def gh(*args: str, stdin: str | None = None, check: bool = True) -> str:
    """Run a `gh` command and return stdout."""
    proc = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, check=False)
    if check and proc.returncode != 0:
        raise GhError(f"gh {' '.join(args[:3])} … failed:\n{proc.stderr.strip()}")
    return proc.stdout


def gh_json(*args: str, stdin: str | None = None):
    out = gh(*args, stdin=stdin)
    return json.loads(out) if out.strip() else None


def graphql(query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}})
    result = gh_json("api", "graphql", "--input", "-", stdin=body)
    if result.get("errors"):
        raise GhError(json.dumps(result["errors"], indent=2))
    return result["data"]


def gql_str(value: str) -> str:
    """Encode a Python string as a GraphQL string literal."""
    return json.dumps(value)


def next_monday(today: dt.date) -> dt.date:
    return today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)


def sprint_schedule(sprints: list[dict], start: dt.date) -> dict[int, tuple[dt.date, int]]:
    """Return {sprint_number: (start_date, duration_days)}."""
    schedule, cursor = {}, start
    for sprint in sprints:
        days = int(sprint.get("weeks", 2)) * 7
        schedule[sprint["number"]] = (cursor, days)
        cursor += dt.timedelta(days=days)
    return schedule


# --------------------------------------------------------------------------- #
# Issue body rendering
# --------------------------------------------------------------------------- #
DOD_BY_TRACK = {
    "default": [  # Backend (Django/API) and Frontend (Django templates + HTMX)
        "Unit & integration tests written (`pytest`) with >= 80% coverage on new code",
        "Linting (`ruff`), security check (`bandit`), and Docker build pass in GitHub Actions",
        "API changes reflected in the OpenAPI schema (`/api/schema/`), if any",
        "Environment variables documented in `.env.example` (if any added)",
        "PR peer-reviewed (>= 1 approval) and linked to this issue",
        "Verified in the Staging environment after PR merge",
    ],
    "Mobile (Flutter)": [
        "Widget/unit tests written; `flutter analyze` and `flutter test` pass in CI",
        "Works against the Staging `/api/v1/` backend (no hard-coded URLs or secrets)",
        "Tested on at least one Android and one iOS (or emulator) target",
        "PR peer-reviewed (>= 1 approval) and linked to this issue",
    ],
    "SPA (React/Angular)": [
        "Unit tests written (Vitest/Karma); ESLint and the production build pass in CI",
        "API client regenerated from the OpenAPI schema (no hand-written drift)",
        "Responsive on mobile & desktop; matches `design.md` tokens",
        "PR peer-reviewed (>= 1 approval) and linked to this issue",
    ],
    "DevOps & Infra": [
        "Pipeline / infrastructure change runs green on a PR before merge",
        "No secrets committed; credentials live in GitHub Actions secrets or environments",
        "Usage / runbook documented in `docs/` or the relevant README",
        "Evidence attached to the PR (workflow run link, screenshot or dashboard)",
        "PR peer-reviewed (>= 1 approval) and linked to this issue",
    ],
}


def render_issue_body(item: dict, sprint: dict) -> str:
    kind = "User Story" if item["id"].startswith("US") else "Engineering Task"
    dod = DOD_BY_TRACK.get(item["track"], DOD_BY_TRACK["default"])
    lines = [
        f"> **Sprint:** {sprint['title']}  ",
        (
            f"> **Track:** {item['track']} · **Story Points:** {item['points']} · "
            f"**Priority:** {item['priority']}"
        ),
        "",
        f"## {kind}",
        item["title"],
        "",
        "## Sprint Goal (context)",
        sprint["goal"],
        "",
        "## Acceptance Criteria",
        *[f"- [ ] {c}" for c in item["acceptance"]],
        "",
        "## DevOps & Quality Definition of Done",
        *[f"- [ ] {d}" for d in dod],
        "",
        "## Branch",
        (
            f"`{'devops' if item['id'].startswith('DO') else 'feat'}/<issue-number>-<short-description>`"
            " — see CONTRIBUTING.md for naming and Conventional Commits."
        ),
        "",
        "---",
        (
            f"<sub>Generated from `scripts/sprint_backlog.json` (ID `{item['id']}`). "
            f"Keep the `[{item['id']}]` title prefix: the setup script uses it to stay idempotent.</sub>"
        ),
    ]
    return "\n".join(lines)


def issue_title(item: dict) -> str:
    return f"[{item['id']}] {item['title']}"


# --------------------------------------------------------------------------- #
# Setup runner
# --------------------------------------------------------------------------- #
class Setup:
    def __init__(self, args: argparse.Namespace, data: dict):
        self.args = args
        self.data = data
        self.repo = args.repo
        self.owner, self.repo_name = args.repo.split("/", 1)
        self.dry = args.dry_run
        self.schedule = sprint_schedule(data["sprints"], args.start_date)
        self.issue_urls: dict[str, str] = {}  # item id -> issue URL

    # ---------------- labels ----------------
    def labels(self) -> None:
        log("\n== Labels ==")
        for label in self.data["labels"]:
            if self.dry:
                log(f"  [dry-run] upsert label {label['name']}")
                continue
            gh(
                "label",
                "create",
                label["name"],
                "-R",
                self.repo,
                "--color",
                label["color"],
                "--description",
                label["description"],
                "--force",
            )
            log(f"  ✓ {label['name']}")

        if self.args.prune_default_labels:
            existing = {
                l["name"]
                for l in gh_json(
                    "label", "list", "-R", self.repo, "--limit", "200", "--json", "name"
                )
            }
            for name in GITHUB_DEFAULT_LABELS:
                if name in existing:
                    if self.dry:
                        log(f"  [dry-run] delete default label {name}")
                    else:
                        gh("label", "delete", name, "-R", self.repo, "--yes")
                        log(f"  ✗ removed default label '{name}'")

    # ---------------- milestones ----------------
    def _existing_milestones(self) -> dict[str, int]:
        ms = gh_json("api", f"repos/{self.repo}/milestones?state=all&per_page=100")
        return {m["title"]: m["number"] for m in ms or []}

    def milestones(self) -> None:
        log("\n== Milestones ==")
        existing = self._existing_milestones()
        for sprint in self.data["sprints"]:
            start, days = self.schedule[sprint["number"]]
            due = start + dt.timedelta(days=days - 1)
            fields = [
                "-f",
                f"title={sprint['title']}",
                "-f",
                f"description=Milestone goal: {sprint['goal']}",
                "-f",
                f"due_on={due.isoformat()}T23:59:59Z",
            ]
            number = existing.get(sprint["title"])
            if self.dry:
                verb = "update" if number else "create"
                log(f"  [dry-run] {verb} milestone '{sprint['title']}' (due {due})")
            elif number:
                gh("api", "-X", "PATCH", f"repos/{self.repo}/milestones/{number}", *fields)
                log(f"  ↻ {sprint['title']} (due {due})")
            else:
                gh("api", "-X", "POST", f"repos/{self.repo}/milestones", *fields)
                log(f"  ✓ {sprint['title']} (due {due})")

    # ---------------- issues ----------------
    def _existing_issues(self) -> dict[str, dict]:
        issues = gh_json(
            "issue",
            "list",
            "-R",
            self.repo,
            "--state",
            "all",
            "--limit",
            "1000",
            "--json",
            "number,title,url",
        )
        by_id = {}
        for issue in issues or []:
            title = issue["title"]
            if title.startswith("[") and "]" in title:
                by_id[title[1 : title.index("]")]] = issue
        return by_id

    def issues(self) -> None:
        log("\n== Issues ==")
        existing = self._existing_issues()
        for sprint in self.data["sprints"]:
            for item in sprint["items"]:
                title, body = issue_title(item), render_issue_body(item, sprint)
                label_args = [a for l in item["labels"] for a in ("--label", l)]
                found = existing.get(item["id"])

                if found and not self.args.update_existing:
                    self.issue_urls[item["id"]] = found["url"]
                    log(f"  • exists  #{found['number']} {item['id']}")
                    continue
                if self.dry:
                    verb = "update" if found else "create"
                    log(f"  [dry-run] {verb} issue {title[:90]}")
                    continue
                if found:
                    gh(
                        "issue",
                        "edit",
                        str(found["number"]),
                        "-R",
                        self.repo,
                        "--title",
                        title,
                        "--body-file",
                        "-",
                        "--milestone",
                        sprint["title"],
                        *[a for l in item["labels"] for a in ("--add-label", l)],
                        stdin=body,
                    )
                    self.issue_urls[item["id"]] = found["url"]
                    log(f"  ↻ updated #{found['number']} {item['id']}")
                else:
                    url = (
                        gh(
                            "issue",
                            "create",
                            "-R",
                            self.repo,
                            "--title",
                            title,
                            "--body-file",
                            "-",
                            "--milestone",
                            sprint["title"],
                            *label_args,
                            stdin=body,
                        )
                        .strip()
                        .splitlines()[-1]
                    )
                    self.issue_urls[item["id"]] = url
                    log(f"  ✓ created {item['id']} → {url}")
                    time.sleep(1)  # stay clear of GitHub's content-creation rate limit

    # ---------------- project ----------------
    def _check_project_scope(self) -> None:
        headers = gh("api", "-i", "user", check=False)
        for line in headers.splitlines():
            if line.lower().startswith("x-oauth-scopes:"):
                scopes = {s.strip() for s in line.split(":", 1)[1].split(",")}
                if "project" not in scopes:
                    raise SystemExit(
                        "\n✗ The active gh token lacks the 'project' scope.\n"
                        "  Run:  gh auth refresh -h github.com -s project\n"
                        "  then re-run this script with --only project"
                    )
                return

    def _find_or_create_project(self) -> tuple[str, int]:
        title = self.data["project"]["title"]
        listing = gh_json(
            "project", "list", "--owner", self.owner, "--format", "json", "--limit", "100"
        )
        for proj in listing.get("projects", []):
            if proj["title"] == title:
                log(f"  • project exists: #{proj['number']} {title}")
                return proj["id"], proj["number"]
        proj = gh_json(
            "project", "create", "--owner", self.owner, "--title", title, "--format", "json"
        )
        log(f"  ✓ created project #{proj['number']} {title}")
        return proj["id"], proj["number"]

    def _project_fields(self, project_id: str) -> dict[str, dict]:
        q = """
        query($id: ID!) { node(id: $id) { ... on ProjectV2 { fields(first: 50) { nodes {
          ... on ProjectV2Field { id name dataType }
          ... on ProjectV2SingleSelectField { id name dataType options { id name } }
          ... on ProjectV2IterationField { id name dataType configuration {
                iterations { id title } completedIterations { id title } } }
        } } } } }"""
        nodes = graphql(q, {"id": project_id})["node"]["fields"]["nodes"]
        return {n["name"]: n for n in nodes if n}

    @staticmethod
    def _options_literal(options: list[dict]) -> str:
        return (
            "["
            + ", ".join(
                f"{{name: {gql_str(o['name'])}, color: {o.get('color', 'GRAY')}, "
                f"description: {gql_str(o.get('description', ''))}}}"
                for o in options
            )
            + "]"
        )

    def _create_single_select(self, project_id: str, name: str, options: list[dict]) -> None:
        graphql(f"""mutation {{ createProjectV2Field(input: {{
            projectId: {gql_str(project_id)}, dataType: SINGLE_SELECT, name: {gql_str(name)},
            singleSelectOptions: {self._options_literal(options)} }}) {{ clientMutationId }} }}""")
        log(f"  ✓ field '{name}' (single select: {', '.join(o['name'] for o in options)})")

    def _ensure_fields(self, project_id: str) -> dict[str, dict]:
        cfg = self.data["project"]
        fields = self._project_fields(project_id)

        # Status: replace the default Todo/In Progress/Done with the roadmap columns.
        status = fields["Status"]
        wanted = [o["name"] for o in cfg["status_options"]]
        if [o["name"] for o in status["options"]] != wanted:
            graphql(f"""mutation {{ updateProjectV2Field(input: {{
                fieldId: {gql_str(status["id"])},
                singleSelectOptions: {self._options_literal(cfg["status_options"])} }})
                {{ clientMutationId }} }}""")
            log(f"  ✓ Status columns → {' → '.join(wanted)}")
        else:
            log("  • Status columns already configured")

        palette = ["BLUE", "GREEN", "YELLOW", "ORANGE", "PURPLE", "PINK", "RED", "GRAY"]
        priority_colors = ["RED", "ORANGE", "YELLOW", "GRAY"]
        for name, values, colors in (
            ("Track", cfg["tracks"], palette),
            ("Priority", cfg["priorities"], priority_colors),
        ):
            if name in fields:
                missing = set(values) - {o["name"] for o in fields[name]["options"]}
                log(
                    f"  • field '{name}' exists"
                    + (f" (⚠ missing options: {sorted(missing)})" if missing else "")
                )
            else:
                self._create_single_select(
                    project_id,
                    name,
                    [
                        {"name": v, "color": colors[i % len(colors)], "description": ""}
                        for i, v in enumerate(values)
                    ],
                )

        if "Story Points" not in fields:
            gh(
                "project",
                "field-create",
                str(self.project_number),
                "--owner",
                self.owner,
                "--name",
                "Story Points",
                "--data-type",
                "NUMBER",
            )
            log("  ✓ field 'Story Points' (number — Fibonacci 1, 2, 3, 5, 8)")
        else:
            log("  • field 'Story Points' exists")

        if "Sprint" not in fields:
            self._create_sprint_field(project_id)
        else:
            log("  • field 'Sprint' exists")

        return self._project_fields(project_id)

    def _create_sprint_field(self, project_id: str) -> None:
        sprints = self.data["sprints"]
        first_start, first_days = self.schedule[sprints[0]["number"]]
        iterations = ", ".join(
            f"{{title: {gql_str(f'Sprint {s["number"]}')}, "
            f"startDate: {gql_str(self.schedule[s['number']][0].isoformat())}, "
            f"duration: {self.schedule[s['number']][1]}}}"
            for s in sprints
        )
        try:
            graphql(f"""mutation {{ createProjectV2Field(input: {{
                projectId: {gql_str(project_id)}, dataType: ITERATION, name: "Sprint",
                iterationConfiguration: {{ startDate: {gql_str(first_start.isoformat())},
                  duration: {first_days}, iterations: [{iterations}] }} }})
                {{ clientMutationId }} }}""")
            log(f"  ✓ field 'Sprint' (iteration: Sprint 0 starts {first_start})")
        except GhError as exc:
            log(f"  ⚠ iteration field not supported by this API ({str(exc)[:120]}…)")
            log("    falling back to a single-select 'Sprint' field")
            self._create_single_select(
                project_id,
                "Sprint",
                [
                    {"name": f"Sprint {s['number']}", "color": "BLUE", "description": s["title"]}
                    for s in sprints
                ],
            )

    def _project_items(self, project_id: str) -> dict[str, str]:
        """Return {issue_url: item_id} for items already on the board."""
        q = """
        query($id: ID!, $after: String) { node(id: $id) { ... on ProjectV2 {
          items(first: 100, after: $after) { pageInfo { hasNextPage endCursor }
            nodes { id content { ... on Issue { url } } } } } } }"""
        items, after = {}, None
        while True:
            page = graphql(q, {"id": project_id, "after": after})["node"]["items"]
            for node in page["nodes"]:
                if node.get("content") and node["content"].get("url"):
                    items[node["content"]["url"]] = node["id"]
            if not page["pageInfo"]["hasNextPage"]:
                return items
            after = page["pageInfo"]["endCursor"]

    @staticmethod
    def _option_id(field: dict, name: str) -> str | None:
        for opt in field.get("options") or []:
            if opt["name"] == name:
                return opt["id"]
        cfg = field.get("configuration") or {}
        for it in cfg.get("iterations", []) + cfg.get("completedIterations", []):
            if it["title"] == name:
                return it["id"]
        return None

    def _set_item_fields(
        self, project_id: str, item_id: str, values: list[tuple[dict, str]]
    ) -> None:
        """values: [(field, graphql value literal)] — all set in one aliased mutation."""
        parts = [
            f"f{i}: updateProjectV2ItemFieldValue(input: {{ projectId: {gql_str(project_id)}, "
            f"itemId: {gql_str(item_id)}, fieldId: {gql_str(field['id'])}, value: {val} }})"
            f" {{ clientMutationId }}"
            for i, (field, val) in enumerate(values)
        ]
        graphql("mutation { " + " ".join(parts) + " }")

    def project(self) -> None:
        log("\n== GitHub Project (v2) ==")
        if self.dry:
            log(
                f"  [dry-run] find/create project '{self.data['project']['title']}' "
                f"for {self.owner}, configure Status/Track/Priority/Story Points/Sprint, "
                f"link to {self.repo}, add {sum(len(s['items']) for s in self.data['sprints'])} issues"
            )
            return
        self._check_project_scope()
        project_id, self.project_number = self._find_or_create_project()

        cfg = self.data["project"]
        readme = (
            Path(__file__).with_name("PROJECT_README.md").read_text()
            if Path(__file__).with_name("PROJECT_README.md").exists()
            else ""
        )
        edit_args = [
            "project",
            "edit",
            str(self.project_number),
            "--owner",
            self.owner,
            "--description",
            cfg["description"],
        ]
        if readme:
            edit_args += ["--readme", readme]
        gh(*edit_args)

        link = subprocess.run(
            [
                "gh",
                "project",
                "link",
                str(self.project_number),
                "--owner",
                self.owner,
                "--repo",
                self.repo_name,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        log(
            "  ✓ linked to repository"
            if link.returncode == 0
            else f"  • link: {link.stderr.strip() or 'already linked'}"
        )

        fields = self._ensure_fields(project_id)

        if not self.issue_urls:  # project phase run on its own
            self.issue_urls = {k: v["url"] for k, v in self._existing_issues().items()}
        on_board = self._project_items(project_id)

        log("\n  Adding issues to the board:")
        first_sprint = self.data["sprints"][0]["number"]
        for sprint in self.data["sprints"]:
            for item in sprint["items"]:
                url = self.issue_urls.get(item["id"])
                if not url:
                    log(f"  ⚠ {item['id']}: no issue found — run the 'issues' phase first")
                    continue
                if url in on_board and not self.args.update_existing:
                    log(f"  • {item['id']} already on board (fields left untouched)")
                    continue
                item_id = (
                    on_board.get(url)
                    or gh_json(
                        "project",
                        "item-add",
                        str(self.project_number),
                        "--owner",
                        self.owner,
                        "--url",
                        url,
                        "--format",
                        "json",
                    )["id"]
                )

                status_name = (
                    cfg["first_sprint_status"]
                    if sprint["number"] == first_sprint
                    else cfg["default_status"]
                )
                values = []
                for fname, opt_name in (
                    ("Status", status_name),
                    ("Track", item["track"]),
                    ("Priority", item["priority"]),
                    ("Sprint", f"Sprint {sprint['number']}"),
                ):
                    field = fields.get(fname)
                    opt = self._option_id(field, opt_name) if field else None
                    if not opt:
                        log(f"    ⚠ {item['id']}: no '{opt_name}' option on field '{fname}'")
                        continue
                    key = (
                        "iterationId"
                        if field["dataType"] == "ITERATION"
                        else "singleSelectOptionId"
                    )
                    values.append((field, f"{{{key}: {gql_str(opt)}}}"))
                if "Story Points" in fields:
                    values.append((fields["Story Points"], f"{{number: {float(item['points'])}}}"))
                self._set_item_fields(project_id, item_id, values)
                log(
                    f"  ✓ {item['id']} · {status_name} · {item['track']} · "
                    f"{item['priority']} · {item['points']} pts · Sprint {sprint['number']}"
                )

        log(f"\n  Board: https://github.com/users/{self.owner}/projects/{self.project_number}")
        log(
            "  Note: Board / Table / Roadmap *views* cannot be created via the API —"
            " add them once in the UI (see scripts/PROJECT_README.md)."
        )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--repo", default=DEFAULT_REPO, help=f"owner/name (default {DEFAULT_REPO})")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA, help="backlog JSON file")
    p.add_argument(
        "--start-date",
        type=dt.date.fromisoformat,
        default=next_monday(dt.date.today()),
        help="Sprint 0 start date, YYYY-MM-DD (default: next Monday)",
    )
    p.add_argument(
        "--only",
        default=",".join(PHASES),
        help=f"comma-separated phases to run: {', '.join(PHASES)}",
    )
    p.add_argument("--dry-run", action="store_true", help="print actions without changing GitHub")
    p.add_argument(
        "--update-existing",
        action="store_true",
        help="refresh existing issues and board items from the JSON (resets field values)",
    )
    p.add_argument(
        "--prune-default-labels",
        action="store_true",
        help="delete GitHub's default labels (bug, enhancement, …)",
    )
    args = p.parse_args()
    args.phases = [x.strip() for x in args.only.split(",") if x.strip()]
    unknown = set(args.phases) - set(PHASES)
    if unknown:
        p.error(f"unknown phase(s): {', '.join(sorted(unknown))}")
    return args


def main() -> int:
    args = parse_args()
    if not shutil.which("gh"):
        log("✗ GitHub CLI (gh) not found — install from https://cli.github.com")
        return 1
    data = json.loads(args.data.read_text())

    total = sum(len(s["items"]) for s in data["sprints"])
    log(f"KamiKon GitHub setup → {args.repo}")
    log(
        f"  {len(data['sprints'])} sprints · {total} backlog items · "
        f"Sprint 0 starts {args.start_date} · phases: {', '.join(args.phases)}"
        + (" · DRY RUN" if args.dry_run else "")
    )

    setup = Setup(args, data)
    try:
        for phase in PHASES:
            if phase in args.phases:
                getattr(setup, phase)()
    except GhError as exc:
        log(f"\n✗ {exc}")
        return 1
    log("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
