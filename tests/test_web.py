from types import SimpleNamespace

from fastapi.testclient import TestClient

from codetrust.web import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/api/health").json() == {"status": "ok", "service": "codetrust"}


def test_dashboard_verifies_diff() -> None:
    response = client.post(
        "/api/verify",
        json={
            "ticket": "Rename label",
            "diff": "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-old=1\n+new=1\n",
            "offline": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["verdict"] == "PASS"


def test_light_intent_map_and_product_tree_are_available() -> None:
    dashboard = client.get("/")
    product = client.get("/api/product-demo")

    assert dashboard.status_code == 200
    assert "Product intent map" in dashboard.text
    assert 'data-view="verification"' in dashboard.text
    assert 'data-testid="real-pr-demo"' in dashboard.text
    assert "switchWorkspaceView" in dashboard.text
    assert "--paper:#f7f7f5" in dashboard.text
    assert product.status_code == 200
    assert product.json()["name"] == "Checkout resilience"
    assert any(node["id"] == "commit-drift" for node in product.json()["nodes"])


def test_real_rejected_pr_demo_verifies_live_diff(monkeypatch) -> None:
    from codetrust.github import PullRequestComment

    monkeypatch.setattr(
        "codetrust.real_pr_demo.load_pull_request",
        lambda _reference: SimpleNamespace(
            diff=(
                "diff --git a/gnucash/gschemas/theme.xml b/gnucash/gschemas/theme.xml\n"
                "--- a/gnucash/gschemas/theme.xml\n"
                "+++ b/gnucash/gschemas/theme.xml\n"
                "@@ -1 +1 @@\n"
                "-<description>GTK theme</description>\n"
                "+<description>Configurable GnuCash light and dark appearance mode</description>\n"
                "diff --git a/gnucash/theme.css b/gnucash/theme.css\n"
                "--- a/gnucash/theme.css\n"
                "+++ b/gnucash/theme.css\n"
                "@@ -1 +1 @@\n"
                "-/* GTK theme */\n"
                "+/* GnuCash dark appearance mode colors */\n"
                "diff --git a/gnucash/preferences.ui b/gnucash/preferences.ui\n"
                "--- a/gnucash/preferences.ui\n"
                "+++ b/gnucash/preferences.ui\n"
                "@@ -1 +1 @@\n"
                "-<label>Theme</label>\n"
                "+<label>Choose Light or Dark appearance mode</label>\n"
            ),
            url="https://github.com/Gnucash/gnucash/pull/2262",
            base_sha="base",
            head_sha="head",
            state="CLOSED",
            merged_at=None,
            closed_at="2026-07-05T19:08:24Z",
            comments=(
                PullRequestComment(
                    author="jralls",
                    association="MEMBER",
                    body="Out of scope, use a Gtk3 theme to configure Light/Dark mode.",
                    url=(
                        "https://github.com/Gnucash/gnucash/pull/2262"
                        "#issuecomment-4887262599"
                    ),
                    created_at="2026-07-05T19:08:24Z",
                ),
            ),
        ),
    )

    preview = client.get("/api/real-pr-demo")
    result = client.post("/api/real-pr-demo/verify")

    assert preview.status_code == 200
    assert preview.json()["name"] == "GnuCash appearance boundary"
    assert result.status_code == 200
    assert result.json()["report"]["verdict"] == "BLOCK"
    assert result.json()["validation"]["agreement"] is True
    assert any(
        finding["rule_id"] == "CT-SCOPE-001"
        for finding in result.json()["report"]["findings"]
    )
    assert any(
        node["id"] == "maintainer-outcome"
        for node in result.json()["product"]["nodes"]
    )


def test_dashboard_routes_interpretation_conflict() -> None:
    response = client.post(
        "/api/verify",
        json={
            "ticket": "## Out of scope\n- Refund authorization behavior.",
            "diff": (
                "diff --git a/refunds/authorization.py b/refunds/authorization.py\n"
                "--- a/refunds/authorization.py\n"
                "+++ b/refunds/authorization.py\n"
                "@@ -1 +1 @@\n-old = 30\n+new = 7\n"
            ),
            "interpretations": [
                {
                    "role": "senior",
                    "text": "Change refund authorization behavior to seven days.",
                    "source": "review",
                }
            ],
            "offline": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["verdict"] == "BLOCK"


def test_creates_product_workspace_and_jira_task(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CODETRUST_DATA_DIR", str(tmp_path))
    created = client.post(
        "/api/workspaces",
        json={
            "name": "Checkout resilience",
            "outcome": "Prevent duplicate charges during retries.",
            "owner": "Maya · Product",
            "in_scope": ["Payment retry handling"],
            "out_of_scope": ["Refund authorization policy"],
            "acceptance_criteria": ["One operation creates at most one charge"],
            "jira_project_key": "PAY",
        },
    )
    assert created.status_code == 201
    product = created.json()

    task = client.post(
        f"/api/workspaces/{product['id']}/nodes",
        json={
            "parent": "product",
            "kind": "jira task",
            "title": "Build retry worker",
            "summary": "Create safe asynchronous payment retry handling.",
            "owner": "Nila · Developer",
            "jira_key": "PAY-1",
        },
    )

    assert task.status_code == 201
    assert task.json()["nodes"][-1]["jira"] == "PAY-1"
    assert client.get("/api/workspaces").json()["products"][0]["id"] == product["id"]


def test_verifies_linked_github_pr_without_raw_diff(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CODETRUST_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(
        "codetrust.web.load_pull_request",
        lambda _reference: SimpleNamespace(
            diff=(
                "diff --git a/ui/label.py b/ui/label.py\n"
                "--- a/ui/label.py\n+++ b/ui/label.py\n"
                "@@ -1 +1 @@\n-old='Pending'\n+new='Awaiting review'\n"
            ),
            url="https://github.com/acme/app/pull/1",
            base_sha="base",
            head_sha="head",
        ),
    )
    product = client.post(
        "/api/workspaces",
        json={
            "name": "Workflow clarity",
            "outcome": "Make review status clear to every project contributor.",
            "owner": "Product owner",
            "in_scope": ["Review status labels"],
            "out_of_scope": ["Payment behavior"],
            "acceptance_criteria": ["Pending review has an understandable label"],
        },
    ).json()
    product = client.post(
        f"/api/workspaces/{product['id']}/nodes",
        json={
            "parent": "product",
            "kind": "commit",
            "title": "Rename pending label",
            "summary": "Clarify review state wording.",
            "owner": "Developer",
            "git_url": "https://github.com/acme/app/pull/1",
        },
    ).json()
    node = product["nodes"][-1]

    result = client.post(f"/api/workspaces/{product['id']}/nodes/{node['id']}/verify")

    assert result.status_code == 200
    assert result.json()["report"]["verdict"] == "PASS"
    assert result.json()["product"]["nodes"][-1]["state"] == "pass"
