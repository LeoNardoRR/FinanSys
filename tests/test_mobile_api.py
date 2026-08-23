from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import SessionLocal
from app.models import Transaction
from main import app


def test_pwa_files_are_available():
    with TestClient(app) as client:
        manifest = client.get("/manifest.webmanifest")
        service_worker = client.get("/service-worker.js")
        dashboard = client.get("/")

    assert manifest.status_code == 200
    assert manifest.json()["display"] == "standalone"
    assert service_worker.status_code == 200
    assert "/api/" in service_worker.text
    assert 'rel="manifest"' in dashboard.text
    assert 'class="mobile-nav"' in dashboard.text


def test_api_dashboard_and_installment_creation():
    description = "Teste API Mobile"
    with TestClient(app) as client:
        dashboard = client.get("/api/v1/dashboard")
        created = client.post("/api/v1/transactions", json={
            "description": description,
            "amount": 100,
            "occurred_on": date.today().isoformat(),
            "kind": "expense",
            "installments_total": 3,
        })

    assert dashboard.status_code == 200
    assert {"income", "expenses", "balance", "recent_transactions"} <= dashboard.json().keys()
    assert created.status_code == 201
    rows = created.json()
    assert len(rows) == 3
    assert sum(row["amount"] for row in rows) == 100
    assert rows[0]["description"].endswith("(1/3)")

    with SessionLocal() as session:
        session.execute(delete(Transaction).where(Transaction.description.like(f"{description}%")))
        session.commit()


def test_pages_preview_is_explicitly_separate():
    root = Path(__file__).resolve().parent.parent
    html = (root / "pages-preview" / "index.html").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "Prévia demonstrativa" in html
    assert "FastAPI não roda no GitHub Pages" in html
    assert "path: pages-preview" in workflow
