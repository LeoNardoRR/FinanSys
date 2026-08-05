from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Card, Category, Goal, Person, Transaction
from app.routes.goals import goal_metrics
from app.services.dashboard import build_dashboard
from app.utils import add_months, invoice_cycle, parse_money


def memory_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_money_and_month_arithmetic():
    assert parse_money("R$ 1.234,56") == Decimal("1234.56")
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_invoice_cycle_before_and_after_closing():
    before = invoice_cycle(date(2026, 8, 3), 10, 17)
    assert before == {"start": date(2026, 7, 11), "end": date(2026, 8, 10), "due": date(2026, 8, 17)}
    after = invoice_cycle(date(2026, 8, 15), 10, 5)
    assert after == {"start": date(2026, 8, 11), "end": date(2026, 9, 10), "due": date(2026, 10, 5)}


def test_goal_projection_metrics():
    goal = Goal(name="Reserva", target_amount=Decimal("12000"), current_amount=Decimal("2000"), monthly_contribution=Decimal("1000"), target_date=date(2027, 6, 1))
    row = goal_metrics(goal)
    assert row["remaining"] == Decimal("10000")
    assert row["months"] == 10
    assert row["projected_12m"] == Decimal("14000")
    assert row["progress"] > 16


def test_dashboard_family_and_person_filters():
    with memory_session() as session:
        person_a = Person(name="Ana")
        person_b = Person(name="Bruno")
        category = Category(name="Mercado", kind="expense")
        session.add_all([person_a, person_b, category])
        session.flush()
        session.add_all([
            Transaction(occurred_on=date(2026, 8, 1), description="Salário Ana", amount=5000, kind="income", person_id=person_a.id),
            Transaction(occurred_on=date(2026, 8, 2), description="Mercado", amount=800, kind="expense", person_id=person_a.id, category_id=category.id),
            Transaction(occurred_on=date(2026, 8, 3), description="Salário Bruno", amount=4000, kind="income", person_id=person_b.id),
            Transaction(occurred_on=date(2026, 8, 4), description="Restaurante", amount=300, kind="expense", person_id=person_b.id),
        ])
        session.commit()
        family = build_dashboard(session, reference_date=date(2026, 8, 10))
        ana = build_dashboard(session, person_id=person_a.id, reference_date=date(2026, 8, 10))
        assert family["income"] == Decimal("9000")
        assert family["expenses"] == Decimal("1100")
        assert ana["income"] == Decimal("5000")
        assert ana["expenses"] == Decimal("800")
        assert len(family["people_metrics"]) == 2


def test_card_alert_uses_current_invoice_cycle():
    with memory_session() as session:
        card = Card(name="Nubank", credit_limit=1000, closing_day=10, due_day=17)
        session.add(card)
        session.flush()
        session.add(Transaction(occurred_on=date(2026, 7, 11), description="Compra", amount=900, kind="expense", card_id=card.id))
        session.commit()
        data = build_dashboard(session, reference_date=date(2026, 8, 3))
        assert any("90%" in alert["text"] for alert in data["alerts"])
