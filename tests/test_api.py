"""Real integration tests against the FastAPI app + an isolated SQLite DB.

Covers the CRUD surface and the cascade behavior of the one-to-many model.
"""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_pain_point_returns_201_and_id(client):
    payload = {
        "title": "Manual AP coding",
        "description": "Bookkeepers re-key invoices into the GL.",
        "category": "AP/AR",
        "firm_size_fit": "mid",
        "severity": "high",
    }
    r = client.post("/pain-points", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    assert body["title"] == payload["title"]
    assert body["solution_count"] == 0


def test_list_pain_points_filter_by_category(client):
    client.post(
        "/pain-points",
        json={
            "title": "Audit prep doc collection",
            "description": "x",
            "category": "Audit",
            "firm_size_fit": "all",
            "severity": "high",
        },
    )
    client.post(
        "/pain-points",
        json={
            "title": "Bank rec matching",
            "description": "x",
            "category": "AP/AR",
            "firm_size_fit": "small",
            "severity": "medium",
        },
    )
    r = client.get("/pain-points?category=AP/AR")
    assert r.status_code == 200
    titles = [p["title"] for p in r.json()]
    assert titles == ["Bank rec matching"]


def test_add_solution_to_pain_point(client):
    pp = client.post(
        "/pain-points",
        json={
            "title": "Manual AP coding",
            "description": "x",
            "category": "AP/AR",
            "firm_size_fit": "mid",
            "severity": "high",
        },
    ).json()

    sol = client.post(
        f"/pain-points/{pp['id']}/solutions",
        json={
            "title": "Claude invoice extraction",
            "description": "OCR + LLM tagging.",
            "tech_stack": "Claude API, Textract",
            "maturity": "prototype",
            "setup_days": 14,
            "pricing_model": "monthly",
            "estimated_price_usd": 1500,
        },
    )
    assert sol.status_code == 201
    assert sol.json()["pain_point_id"] == pp["id"]

    # Detail endpoint should include the solution
    detail = client.get(f"/pain-points/{pp['id']}").json()
    assert detail["solution_count"] == 1
    assert len(detail["solutions"]) == 1
    assert detail["solutions"][0]["title"] == "Claude invoice extraction"


def test_delete_pain_point_cascades_to_solutions(client):
    pp = client.post(
        "/pain-points",
        json={
            "title": "x",
            "description": "x",
            "category": "AP/AR",
            "firm_size_fit": "all",
            "severity": "low",
        },
    ).json()
    client.post(
        f"/pain-points/{pp['id']}/solutions",
        json={"title": "s1", "description": "x"},
    )
    client.post(
        f"/pain-points/{pp['id']}/solutions",
        json={"title": "s2", "description": "x"},
    )

    # Delete the parent
    r = client.delete(f"/pain-points/{pp['id']}")
    assert r.status_code == 200

    # Children should be gone
    r = client.get(f"/pain-points/{pp['id']}")
    assert r.status_code == 404


def test_update_pain_point_partial(client):
    pp = client.post(
        "/pain-points",
        json={
            "title": "x",
            "description": "x",
            "category": "Tax",
            "firm_size_fit": "small",
            "severity": "low",
        },
    ).json()

    r = client.put(
        f"/pain-points/{pp['id']}", json={"severity": "high"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["severity"] == "high"
    assert body["category"] == "Tax"  # untouched


def test_404_on_unknown_pain_point(client):
    r = client.get("/pain-points/99999")
    assert r.status_code == 404


def test_stats_endpoint(client):
    client.post(
        "/pain-points",
        json={
            "title": "x",
            "description": "x",
            "category": "AP/AR",
            "firm_size_fit": "small",
            "severity": "high",
        },
    )
    r = client.get("/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["pain_point_total"] == 1
    assert body["solution_total"] == 0
    assert body["pain_points_by_category"] == {"AP/AR": 1}
