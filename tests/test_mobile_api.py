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


def test_pages_app_uses_supabase_and_is_built_separately():
    root = Path(__file__).resolve().parent.parent
    html = (root / "pages-preview" / "index.html").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    source = (root / "pages-preview" / "src" / "app.js").read_text(encoding="utf-8")
    assert 'id="login-form"' in html
    assert "supabase.co" in html
    assert "createClient" in source
    assert "service_role" not in source.lower()
    assert 'id="forecast-date"' in html
    assert 'id="filter-date-start"' in html
    assert 'id="filter-date-end"' in html
    assert "renderForecast" in source
    assert "🔒" not in html
    assert "npm run build" in workflow
    assert "path: pages-preview" in workflow


def test_pages_auth_has_resilient_feedback_and_accessible_controls():
    root = Path(__file__).resolve().parent.parent / "pages-preview"
    html = (root / "index.html").read_text(encoding="utf-8")
    source = (root / "src" / "app.js").read_text(encoding="utf-8")
    worker = (root / "service-worker.js").read_text(encoding="utf-8")

    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert html.count("data-password-toggle=") == 4
    assert "runAuth" in source
    assert "withTimeout" in source
    assert "finally" in source
    assert 'error?.code === "invalid_credentials"' in source
    assert 'error?.code === "email_not_confirmed"' in source
    assert "form.toggleAttribute(\"aria-busy\", busy)" in source
    assert "finansys-app-v9" in worker
    assert "styles.css?v=9" in html
    assert "app.js?v=9" in html
