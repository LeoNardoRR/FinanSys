from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.models import Card, Category, PaymentMethod, Person, PlannedExpense, Purchase, Transaction
from main import app


def test_large_product_purchase_creates_exact_linked_installments():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    local_session = sessionmaker(engine, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with local_session() as session:
        card = Card(name="Cartão X", credit_limit=10000, closing_day=10, due_day=17)
        category = Category(name="Compras", kind="expense")
        credit = PaymentMethod(name="Crédito")
        person = Person(name="Pessoa Teste")
        planned = PlannedExpense(description="Geladeira", amount=Decimal("4999.99"), expected_on=date(2026, 8, 15), person_id=None)
        session.add_all([card, category, credit, person, planned])
        session.commit()
        ids = {"card": card.id, "category": category.id, "person": person.id, "planned": planned.id}

    def override_session():
        with local_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as client:
            response = client.post("/purchases", data={
                "product_name": "Geladeira Frost Free", "store_name": "Loja Casa",
                "total_amount": "4.999,99", "purchased_on": "2026-08-15",
                "installments_total": "5", "card_id": str(ids["card"]),
                "category_id": str(ids["category"]), "person_id": str(ids["person"]),
                "warranty_months": "12", "notes": "Pedido 123",
                "planned_expense_id": str(ids["planned"]),
            }, follow_redirects=False)
            assert response.status_code == 303
            assert response.headers["location"] == "/purchases?saved=1"

            with local_session() as session:
                purchase = session.scalar(select(Purchase))
                installments = session.scalars(select(Transaction).order_by(Transaction.installment_number)).all()
                planned = session.get(PlannedExpense, ids["planned"])
                assert purchase.product_name == "Geladeira Frost Free"
                assert purchase.first_due_on == date(2026, 9, 17)
                assert purchase.last_due_on == date(2027, 1, 17)
                assert purchase.warranty_until == date(2027, 8, 15)
                assert len(installments) == 5
                assert sum((item.amount for item in installments), Decimal(0)) == Decimal("4999.99")
                assert [item.amount for item in installments] == [Decimal("1000.00")] * 4 + [Decimal("999.99")]
                assert all(item.purchase_id == purchase.id for item in installments)
                assert all(item.card_id == ids["card"] for item in installments)
                assert planned.status == "converted"
                purchase_id = purchase.id

            page = client.get("/purchases")
            assert page.status_code == 200
            assert "Geladeira Frost Free" in page.text
            assert "5x de R$ 1000,00" in page.text
            assert "17/01/2027" in page.text

            protected = client.post(f"/transactions/{installments[0].id}/delete", follow_redirects=False)
            assert protected.status_code == 303
            assert protected.headers["location"] == "/purchases?protected=1"

            deleted = client.post(f"/purchases/{purchase_id}/delete", follow_redirects=False)
            assert deleted.status_code == 303
            with local_session() as session:
                assert session.scalar(select(Purchase)) is None
                assert session.scalars(select(Transaction)).all() == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
