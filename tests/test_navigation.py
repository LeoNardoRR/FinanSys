from fastapi.testclient import TestClient
from main import app


def test_all_pages_and_exports_load():
    paths = ["/", "/transactions", "/purchases", "/cards", "/goals", "/subscriptions", "/cash-flow", "/planning", "/settings", "/help"]
    with TestClient(app) as client:
        for path in paths:
            response = client.get(path)
            assert response.status_code == 200, path
            assert "FinanSys" in response.text
            assert "�" not in response.text
        assert client.get("/reports/transactions.csv").status_code == 200
        xlsx = client.get("/reports/transactions.xlsx")
        assert xlsx.status_code == 200
        assert xlsx.content[:2] == b"PK"
        pdf = client.get("/reports/summary.pdf")
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")
