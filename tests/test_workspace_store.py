from codetrust.workspace_store import add_node, create_product, list_products, record_verification


def test_product_and_work_nodes_persist(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CODETRUST_DATA_DIR", str(tmp_path))
    product = create_product(
        {
            "name": "Checkout resilience",
            "outcome": "Prevent duplicate charges during retries.",
            "owner": "Product owner",
            "in_scope": ["Payment retry handling"],
            "out_of_scope": ["Refund authorization policy"],
            "acceptance_criteria": ["One operation creates one charge"],
            "jira_project_key": "PAY",
            "jira_project_url": "https://jira.example/browse/PAY",
        }
    )
    product = add_node(
        product["id"],
        {
            "parent": "product",
            "kind": "commit",
            "title": "Retry worker",
            "summary": "Implement safe payment retry worker.",
            "owner": "Developer",
            "jira_key": "PAY-1",
            "git_url": "https://github.com/acme/payments/pull/7",
        },
    )
    node = product["nodes"][-1]
    product = record_verification(
        product["id"],
        node["id"],
        {"verdict": "PASS", "risk_score": 0, "findings": []},
    )

    assert list_products()[0]["name"] == "Checkout resilience"
    assert product["nodes"][-1]["state"] == "pass"
    assert product["summary"]["commits"] == 1
