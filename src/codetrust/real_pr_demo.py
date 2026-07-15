from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from codetrust.agent import verify_change
from codetrust.github import PullRequestChange, load_pull_request
from codetrust.models import InterpretationClaim, VerificationReport
from codetrust.report import write_reports

REAL_PR_REFERENCE = "Gnucash/gnucash#2262"
REAL_PR_URL = "https://github.com/Gnucash/gnucash/pull/2262"
REAL_PR_POLICY_URL = "https://wiki.gnucash.org/wiki/GTK3#Dark_Themes"

REAL_PR_INTENT = """# Preserve GTK3 theme ownership

## Outcome
Keep light and dark appearance controlled by GTK3 themes.

## In scope
- GTK3 theme configuration.

## Out of scope
- Configurable light/dark appearance mode inside GnuCash.

## Acceptance criteria
- Appearance remains GTK3 theme-controlled.
"""

REAL_PR_DEVELOPER_INTERPRETATION = (
    "Add a configurable GnuCash appearance mode with System, Light, and Dark choices."
)

_BASE_TREE = {
    "name": "GnuCash appearance boundary",
    "tagline": "Live public PR #2262 checked against explicit maintainer scope.",
    "summary": {"coverage": 0, "drift": 0, "decisions": "hidden", "commits": 1},
    "nodes": [
        {
            "id": "product",
            "parent": None,
            "kind": "repository intent",
            "title": "GTK3 owns light and dark appearance",
            "summary": (
                "GnuCash delegates appearance to GTK3 themes instead of owning a separate "
                "application theme system."
            ),
            "owner": "GnuCash maintainers",
            "state": "approved",
            "alignment": 100,
            "jira": "Public policy",
            "original": "Use GTK3 theme configuration for Light/Dark mode.",
            "current": "Structured product boundary ready for verification.",
            "evidence": f"Repository guidance · {REAL_PR_POLICY_URL}",
            "action": "Check proposed code against this boundary before reading final outcome.",
        },
        {
            "id": "scope-contract",
            "parent": "product",
            "kind": "scope contract",
            "title": "Keep appearance theme-controlled",
            "summary": "Allow GTK3 theme configuration; reject application-owned appearance mode.",
            "owner": "CodeTrust · Policy input",
            "state": "approved",
            "alignment": 100,
            "jira": "GTK3",
            "original": "GTK3 theme configuration is in scope.",
            "current": "GnuCash-owned System/Light/Dark selection is out of scope.",
            "evidence": "Human boundary converted to structured intent; not model-generated evidence.",
            "action": "Fetch live PR diff and test changed surfaces against boundary.",
        },
        {
            "id": "real-pr",
            "parent": "scope-contract",
            "kind": "commit",
            "title": "PR #2262 · Configurable dark appearance mode",
            "summary": (
                "Public pull request adds application preferences, platform detection, custom "
                "colors, and report styling."
            ),
            "owner": "copystring · Contributor",
            "state": "needs review",
            "alignment": 50,
            "jira": "GitHub #2262",
            "git_url": REAL_PR_URL,
            "original": "Appearance remains controlled by GTK3 themes.",
            "current": "Contributor proposes GnuCash-owned System, Light, and Dark choices.",
            "evidence": "Live public diff fetched through fixed GitHub CLI commands at run time.",
            "action": "Run CodeTrust. Maintainer outcome stays hidden until verdict exists.",
        },
    ],
}


def load_and_verify_real_pr() -> tuple[PullRequestChange, VerificationReport, dict]:
    change = load_pull_request(REAL_PR_REFERENCE)
    maintainer_decision = find_maintainer_decision(change)
    report = verify_change(
        REAL_PR_INTENT,
        change.diff,
        offline=True,
        source={
            "type": "github-pr",
            "reference": REAL_PR_REFERENCE,
            "url": change.url,
            "base_sha": change.base_sha,
            "head_sha": change.head_sha,
            "policy_url": REAL_PR_POLICY_URL,
        },
        interpretations=[
            InterpretationClaim(
                role="developer",
                text=REAL_PR_DEVELOPER_INTERPRETATION,
                source=change.url,
            )
        ],
    )
    validation = {
        **maintainer_decision,
        "pr_state": change.state,
        "merged": change.merged_at is not None,
        "closed_at": change.closed_at,
        "agreement": (
            report.verdict.value == "BLOCK"
            and change.state == "CLOSED"
            and change.merged_at is None
        ),
    }
    return change, report, validation


def find_maintainer_decision(change: PullRequestChange) -> dict[str, str]:
    trusted_associations = {"OWNER", "MEMBER", "COLLABORATOR"}
    decision = next(
        (
            comment
            for comment in change.comments
            if comment.association in trusted_associations
            and "out of scope" in comment.body.lower()
        ),
        None,
    )
    if decision is None:
        raise RuntimeError("Public maintainer scope decision is unavailable")
    return {
        "author": decision.author,
        "association": decision.association,
        "quote": decision.body,
        "url": decision.url,
        "created_at": decision.created_at,
    }


def real_pr_product_tree(
    report: VerificationReport | None = None,
    validation: dict | None = None,
) -> dict:
    tree = deepcopy(_BASE_TREE)
    if report is None:
        return tree

    scope_findings = [item for item in report.findings if item.rule_id == "CT-SCOPE-001"]
    changed_paths = sorted({item.path for item in scope_findings})
    tree["summary"] = {
        "coverage": report.scope_coverage or 0,
        "drift": report.scope_drift,
        "decisions": 1,
        "commits": 1,
    }
    commit = next(item for item in tree["nodes"] if item["id"] == "real-pr")
    commit.update(
        {
            "state": "blocked" if report.verdict.value == "BLOCK" else "needs review",
            "alignment": max(0, 100 - report.scope_drift),
            "evidence": (
                f"{len(scope_findings)} scope finding(s) across {len(changed_paths)} file(s); "
                f"risk {report.risk_score}/100."
            ),
            "action": "Compare CodeTrust verdict with public maintainer outcome.",
        }
    )

    if validation:
        tree["nodes"].append(
            {
                "id": "maintainer-outcome",
                "parent": "real-pr",
                "kind": "external validation",
                "title": "Maintainer also rejected PR as out of scope",
                "summary": "GitHub outcome revealed after CodeTrust produced its verdict.",
                "owner": f"{validation['author']} · {validation['association'].title()}",
                "state": "validated" if validation["agreement"] else "needs review",
                "alignment": 100 if validation["agreement"] else 0,
                "jira": "Closed · unmerged" if not validation["merged"] else "Merged",
                "git_url": validation["url"],
                "original": f"CodeTrust verdict: {report.verdict.value}.",
                "current": validation["quote"],
                "evidence": validation["url"],
                "action": (
                    "Use as external validation case. Do not claim universal detection accuracy."
                ),
            }
        )
    return tree


def main() -> int:
    _change, report, validation = load_and_verify_real_pr()
    paths = write_reports(report, Path("reports/real-pr-gnucash-2262"))
    print(
        f"{report.verdict.value} · risk {report.risk_score}/100 · "
        f"scope drift {report.scope_drift}%"
    )
    print(
        "EXTERNAL MATCH"
        if validation["agreement"]
        else "EXTERNAL OUTCOME DOES NOT MATCH CODETRUST VERDICT"
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
