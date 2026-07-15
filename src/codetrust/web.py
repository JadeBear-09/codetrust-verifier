from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from codetrust.agent import verify_change
from codetrust.demo_product import DEMO_PRODUCT_TREE
from codetrust.github import load_pull_request
from codetrust.models import InterpretationClaim
from codetrust.real_pr_demo import (
    load_and_verify_real_pr,
    real_pr_product_tree,
)
from codetrust.ui import LIGHT_DASHBOARD_HTML
from codetrust.workspace_store import (
    add_node,
    create_product,
    get_product,
    list_products,
    record_verification,
)


class InterpretationInput(BaseModel):
    role: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=4_000)
    source: str = Field(default="", max_length=500)


class VerifyRequest(BaseModel):
    ticket: str = Field(min_length=1, max_length=20_000)
    diff: str = Field(min_length=1, max_length=500_000)
    offline: bool = True
    interpretations: list[InterpretationInput] = Field(default_factory=list, max_length=20)


class GitHubRequest(BaseModel):
    reference: str = Field(min_length=3, max_length=500)
    offline: bool = True


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    outcome: str = Field(min_length=10, max_length=4_000)
    owner: str = Field(min_length=2, max_length=200)
    in_scope: list[str] = Field(min_length=1, max_length=30)
    out_of_scope: list[str] = Field(default_factory=list, max_length=30)
    acceptance_criteria: list[str] = Field(min_length=1, max_length=50)
    jira_project_key: str = Field(default="", max_length=50)
    jira_project_url: str = Field(default="", max_length=1_000)


class WorkNodeCreateRequest(BaseModel):
    parent: str = Field(min_length=1, max_length=100)
    kind: str = Field(pattern=r"^(jira task|commit|decision)$")
    title: str = Field(min_length=2, max_length=250)
    summary: str = Field(min_length=5, max_length=4_000)
    owner: str = Field(min_length=2, max_length=200)
    jira_key: str = Field(default="", max_length=100)
    jira_url: str = Field(default="", max_length=1_000)
    commit: str = Field(default="", max_length=100)
    git_url: str = Field(default="", max_length=1_000)
    interpretation_role: str = Field(default="developer", max_length=80)
    interpretation: str = Field(default="", max_length=4_000)
    product_clause: str = Field(default="", max_length=4_000)
    current_change: str = Field(default="", max_length=4_000)


app = FastAPI(
    title="CodeTrust",
    version="0.2.0",
    description="Evidence-first verification API for AI-generated changes.",
)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return LIGHT_DASHBOARD_HTML


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "codetrust"}


@app.get("/api/demo")
def demo() -> dict[str, str]:
    root = Path.cwd()
    ticket = root / "demo/tickets/payment-reconciliation.md"
    diff = root / "demo/patches/risky-payment.diff"
    if not ticket.exists() or not diff.exists():
        raise HTTPException(status_code=404, detail="Run server from CodeTrust repository root")
    return {"ticket": ticket.read_text(), "diff": diff.read_text()}


@app.get("/api/product-demo")
def product_demo() -> dict:
    return DEMO_PRODUCT_TREE


@app.get("/api/real-pr-demo")
def real_pr_demo() -> dict:
    return real_pr_product_tree()


@app.post("/api/real-pr-demo/verify")
def verify_real_pr_demo() -> dict:
    try:
        _change, report, validation = load_and_verify_real_pr()
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "product": real_pr_product_tree(report, validation),
        "report": report.to_dict(),
        "validation": validation,
    }


@app.get("/api/workspaces")
def workspaces() -> dict[str, list[dict]]:
    return {"products": list_products()}


@app.post("/api/workspaces", status_code=201)
def new_workspace(request: ProductCreateRequest) -> dict:
    return create_product(request.model_dump())


@app.post("/api/workspaces/{product_id}/nodes", status_code=201)
def new_work_node(product_id: str, request: WorkNodeCreateRequest) -> dict:
    try:
        return add_node(product_id, request.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/workspaces/{product_id}/nodes/{node_id}/verify")
def verify_work_node(product_id: str, node_id: str) -> dict:
    try:
        product = get_product(product_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    node = next((item for item in product["nodes"] if item["id"] == node_id), None)
    if node is None:
        raise HTTPException(status_code=404, detail="Work node not found")
    if not node.get("git_url"):
        raise HTTPException(status_code=400, detail="Link a GitHub pull request before verification")
    try:
        change = load_pull_request(node["git_url"])
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    claims = []
    if node.get("interpretation"):
        claims.append(
            InterpretationClaim(
                role=node.get("interpretation_role") or "developer",
                text=node["interpretation"],
                source=node.get("git_url") or "workspace",
            )
        )
    report = verify_change(
        _ticket_from_product(product),
        change.diff,
        offline=True,
        source={
            "type": "github-pr",
            "url": change.url,
            "base_sha": change.base_sha,
            "head_sha": change.head_sha,
        },
        interpretations=claims,
    ).to_dict()
    updated = record_verification(product_id, node_id, report)
    return {"product": updated, "report": report}


@app.post("/api/verify")
def verify(request: VerifyRequest) -> dict:
    return verify_change(
        request.ticket,
        request.diff,
        offline=request.offline,
        source={"type": "dashboard-diff"},
        interpretations=[
            InterpretationClaim(role=item.role, text=item.text, source=item.source)
            for item in request.interpretations
        ],
    ).to_dict()


@app.post("/api/github")
def verify_github(request: GitHubRequest) -> dict:
    try:
        change = load_pull_request(request.reference)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return verify_change(
        change.ticket,
        change.diff,
        offline=request.offline,
        source={
            "type": "github-pr",
            "reference": request.reference,
            "url": change.url,
            "base_sha": change.base_sha,
            "head_sha": change.head_sha,
        },
    ).to_dict()


def run_server(host: str, port: int) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port, log_level="info")


def _ticket_from_product(product: dict) -> str:
    def section(title: str, values: list[str]) -> str:
        body = "\n".join(f"- {item}" for item in values)
        return f"## {title}\n{body}" if body else ""

    return "\n\n".join(
        item
        for item in [
            f"# {product['name']}",
            f"## Outcome\n{product['outcome']}",
            section("In scope", product["in_scope"]),
            section("Out of scope", product["out_of_scope"]),
            section("Acceptance criteria", product["acceptance_criteria"]),
        ]
        if item
    )
