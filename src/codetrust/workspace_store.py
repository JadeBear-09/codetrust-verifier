from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

_LOCK = threading.Lock()


def list_products() -> list[dict]:
    with _LOCK:
        return _read_state()["products"]


def get_product(product_id: str) -> dict:
    with _LOCK:
        return _find_product(_read_state(), product_id)


def create_product(data: dict) -> dict:
    with _LOCK:
        state = _read_state()
        product_id = f"product-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(UTC).isoformat()
        root = {
            "id": "product",
            "parent": None,
            "kind": "product intent",
            "title": data["name"],
            "summary": data["outcome"],
            "owner": data["owner"],
            "state": "approved",
            "alignment": 100,
            "jira": data.get("jira_project_key") or "Not linked",
            "jira_url": data.get("jira_project_url") or "",
            "original": data["outcome"],
            "current": "Approved product intent · revision 1",
            "evidence": (
                f"{len(data['acceptance_criteria'])} acceptance criteria and "
                f"{len(data['out_of_scope'])} explicit product boundaries."
            ),
            "action": "Create work branches; revise intent only through product decision.",
        }
        product = {
            "id": product_id,
            "name": data["name"],
            "tagline": data["outcome"],
            "owner": data["owner"],
            "revision": 1,
            "created_at": created_at,
            "outcome": data["outcome"],
            "in_scope": data["in_scope"],
            "out_of_scope": data["out_of_scope"],
            "acceptance_criteria": data["acceptance_criteria"],
            "jira_project_key": data.get("jira_project_key") or "",
            "jira_project_url": data.get("jira_project_url") or "",
            "summary": {"coverage": 100, "drift": 0, "decisions": 0, "commits": 0},
            "nodes": [root],
        }
        state["products"].append(product)
        _write_state(state)
        return product


def add_node(product_id: str, data: dict) -> dict:
    with _LOCK:
        state = _read_state()
        product = _find_product(state, product_id)
        if not any(node["id"] == data["parent"] for node in product["nodes"]):
            raise KeyError("Parent node not found")
        kind = data["kind"]
        node = {
            "id": f"node-{uuid.uuid4().hex[:8]}",
            "parent": data["parent"],
            "kind": kind,
            "title": data["title"],
            "summary": data["summary"],
            "owner": data["owner"],
            "state": "unverified" if kind == "commit" else "planned",
            "alignment": 0,
            "jira": data.get("jira_key") or "Not linked",
            "jira_url": data.get("jira_url") or "",
            "commit": data.get("commit") or "",
            "git_url": data.get("git_url") or "",
            "interpretation_role": data.get("interpretation_role") or "developer",
            "interpretation": data.get("interpretation") or "",
            "original": data.get("product_clause") or product["outcome"],
            "current": data.get("current_change") or data["summary"],
            "evidence": "Awaiting CodeTrust verification.",
            "action": (
                "Link GitHub pull request and run verification."
                if kind == "commit"
                else "Break task into implementation commits."
            ),
        }
        product["nodes"].append(node)
        _refresh_summary(product)
        _write_state(state)
        return product


def record_verification(product_id: str, node_id: str, report: dict) -> dict:
    with _LOCK:
        state = _read_state()
        product = _find_product(state, product_id)
        node = next((item for item in product["nodes"] if item["id"] == node_id), None)
        if node is None:
            raise KeyError("Work node not found")
        verdict = report["verdict"]
        node["state"] = {"PASS": "pass", "NEEDS_REVIEW": "needs review", "BLOCK": "blocked"}[
            verdict
        ]
        node["alignment"] = {"PASS": 100, "NEEDS_REVIEW": 55, "BLOCK": 15}[verdict]
        node["evidence"] = (
            f"CodeTrust {verdict} · risk {report['risk_score']}/100 · "
            f"{len(report['findings'])} finding(s)."
        )
        node["action"] = {
            "PASS": "Technical evidence supports merge review.",
            "NEEDS_REVIEW": "Resolve product or senior-review question before merge.",
            "BLOCK": "Fix blocking evidence, push new commit, then rerun.",
        }[verdict]
        node["verification"] = report
        _refresh_summary(product)
        _write_state(state)
        return product


def _data_path() -> Path:
    configured = os.getenv("CODETRUST_DATA_DIR")
    root = Path(configured) if configured else Path.cwd() / ".codetrust"
    return root / "workspaces.json"


def _read_state() -> dict:
    path = _data_path()
    if not path.exists():
        return {"products": []}
    return json.loads(path.read_text())


def _write_state(state: dict) -> None:
    path = _data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(path)


def _find_product(state: dict, product_id: str) -> dict:
    product = next((item for item in state["products"] if item["id"] == product_id), None)
    if product is None:
        raise KeyError("Product workspace not found")
    return product


def _refresh_summary(product: dict) -> None:
    nodes = [node for node in product["nodes"] if node["kind"] != "product intent"]
    verified = [node for node in nodes if node["alignment"] > 0]
    coverage = round(sum(node["alignment"] for node in verified) / len(verified)) if verified else 0
    drifted = [node for node in verified if node["alignment"] < 50]
    drift = round(len(drifted) / len(verified) * 100) if verified else 0
    product["summary"] = {
        "coverage": coverage,
        "drift": drift,
        "decisions": sum(node["state"] == "needs review" for node in nodes),
        "commits": sum(node["kind"] == "commit" for node in nodes),
    }
