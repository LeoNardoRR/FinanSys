from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.models import Category, Goal, Person, Subscription, Transaction
from main import app


def test_complete_local_workflow():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    local_session = sessionmaker(engine, expire_on_commit=False)

    def override_session():
        with local_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as client:
            assert client.post("/planning/person", data={"name": "Ana"}, follow_redirects=False).status_code == 303
            with local_session() as session:
                person = session.scalar(select(Person).where(Person.name == "Ana"))
                category = Category(name="Casa", kind="expense")
                session.add(category)
                session.commit()
                person_id, category_id = person.id, category.id

            response = client.post("/transactions", data={
                "description": "Móvel", "amount": "100,00", "occurred_on": "2026-08-03",
                "kind": "expense", "category_id": str(category_id), "person_id": str(person_id),
                "installments_total": "3", "notes": "Teste de parcelas",
            }, follow_redirects=False)
            assert response.status_code == 303
            with local_session() as session:
                rows = session.scalars(select(Transaction).order_by(Transaction.installment_number)).all()
                assert [row.amount for row in rows] == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]
                assert [row.occurred_on for row in rows] == [date(2026, 8, 3), date(2026, 9, 3), date(2026, 10, 3)]
                first_id = rows[0].id

            assert client.post(f"/transactions/{first_id}/edit", data={
                "description": "Móvel editado", "amount": "35,00", "occurred_on": "2026-08-04",
                "kind": "expense", "category_id": str(category_id), "person_id": str(person_id), "notes": "Editado",
            }, follow_redirects=False).status_code == 303

            assert client.post("/goals", data={
                "name": "Viagem", "target_amount": "12000", "current_amount": "2000",
                "monthly_contribution": "1000", "target_date": "2027-08-01",
            }, follow_redirects=False).status_code == 303

            assert client.post("/subscriptions", data={
                "name": "Streaming", "amount": "39,90", "billing_day": "12", "person_id": str(person_id),
            }, follow_redirects=False).status_code == 303
            assert client.post("/subscriptions/generate", data={"month": "8", "year": "2026"}, follow_redirects=False).status_code == 303
            assert client.post("/subscriptions/generate", data={"month": "8", "year": "2026"}, follow_redirects=False).status_code == 303
            with local_session() as session:
                generated = session.scalars(select(Transaction).where(Transaction.description == "Streaming")).all()
                assert len(generated) == 1
                assert session.scalar(select(Goal).where(Goal.name == "Viagem")) is not None
                assert session.scalar(select(Subscription).where(Subscription.name == "Streaming")) is not None

            for path in ["/", "/transactions", "/goals", "/subscriptions", "/planning"]:
                assert client.get(path).status_code == 200
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
