from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Bank, Card, Category, Goal, PaymentMethod, Person, Subscription, Transaction
from app.services.dashboard import build_dashboard
from app.settings import API_TOKEN
from app.utils import add_months

router = APIRouter(prefix="/api/v1", tags=["api"])


def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    if API_TOKEN and x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token da API inválido.")


ApiAccess = Depends(require_api_token)


class TransactionCreate(BaseModel):
    description: str = Field(min_length=1, max_length=160)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    occurred_on: date
    kind: str
    category_id: int | None = None
    bank_id: int | None = None
    payment_method_id: int | None = None
    card_id: int | None = None
    person_id: int | None = None
    installments_total: int = Field(default=1, ge=1, le=120)
    notes: str | None = Field(default=None, max_length=2000)


def money(value: Decimal) -> float:
    return float(Decimal(value or 0))


def transaction_json(item: Transaction) -> dict:
    return {
        "id": item.id,
        "occurred_on": item.occurred_on.isoformat(),
        "description": item.description,
        "amount": money(item.amount),
        "kind": item.kind,
        "category_id": item.category_id,
        "bank_id": item.bank_id,
        "payment_method_id": item.payment_method_id,
        "card_id": item.card_id,
        "person_id": item.person_id,
        "installment_number": item.installment_number,
        "installments_total": item.installments_total,
        "notes": item.notes,
    }


@router.get("/dashboard", dependencies=[ApiAccess])
def api_dashboard(person_id: int | None = None, session: Session = Depends(get_session)):
    data = build_dashboard(session, person_id=person_id)
    return {
        "month": data["month_label"],
        "income": money(data["income"]),
        "expenses": money(data["expenses"]),
        "balance": money(data["balance"]),
        "monthly_goal": money(data["monthly_goal"]),
        "goal_percent": data["goal_percent"],
        "category_labels": data["category_labels"],
        "category_values": data["category_values"],
        "recent_transactions": [transaction_json(item) for item in data["recent_transactions"]],
        "alerts": data["alerts"],
    }


@router.get("/transactions", dependencies=[ApiAccess])
def api_transactions(limit: int = 50, session: Session = Depends(get_session)):
    limit = min(max(limit, 1), 200)
    items = session.scalars(
        select(Transaction).order_by(Transaction.occurred_on.desc(), Transaction.id.desc()).limit(limit)
    ).all()
    return [transaction_json(item) for item in items]


@router.post("/transactions", status_code=201, dependencies=[ApiAccess])
def api_create_transaction(payload: TransactionCreate, session: Session = Depends(get_session)):
    if payload.kind not in {"income", "expense"}:
        raise HTTPException(status_code=422, detail="Tipo inválido.")
    description = payload.description.strip()
    if not description:
        raise HTTPException(status_code=422, detail="Informe a descrição.")
    total = Decimal(payload.amount)
    group = str(uuid4()) if payload.installments_total > 1 else None
    installment_value = (total / payload.installments_total).quantize(Decimal("0.01"))
    distributed = Decimal(0)
    created = []
    for number in range(1, payload.installments_total + 1):
        value = total - distributed if number == payload.installments_total else installment_value
        distributed += value
        suffix = f" ({number}/{payload.installments_total})" if group else ""
        item = Transaction(
            description=description + suffix,
            amount=value,
            occurred_on=add_months(payload.occurred_on, number - 1),
            kind=payload.kind,
            category_id=payload.category_id,
            bank_id=payload.bank_id,
            payment_method_id=payload.payment_method_id,
            card_id=payload.card_id,
            person_id=payload.person_id,
            installment_number=number if group else None,
            installments_total=payload.installments_total if group else None,
            installment_group=group,
            notes=payload.notes.strip() if payload.notes else None,
        )
        session.add(item)
        created.append(item)
    session.commit()
    return [transaction_json(item) for item in created]


@router.get("/lookups", dependencies=[ApiAccess])
def api_lookups(session: Session = Depends(get_session)):
    def rows(model):
        return [
            {"id": item.id, "name": item.name}
            for item in session.scalars(select(model).where(model.active.is_(True)).order_by(model.name)).all()
        ]

    return {
        "categories": rows(Category),
        "banks": rows(Bank),
        "cards": rows(Card),
        "payment_methods": rows(PaymentMethod),
        "people": rows(Person),
    }


@router.get("/cards", dependencies=[ApiAccess])
def api_cards(session: Session = Depends(get_session)):
    return [
        {
            "id": item.id,
            "name": item.name,
            "brand": item.brand,
            "credit_limit": money(item.credit_limit),
            "closing_day": item.closing_day,
            "due_day": item.due_day,
        }
        for item in session.scalars(select(Card).where(Card.active.is_(True)).order_by(Card.name)).all()
    ]


@router.get("/goals", dependencies=[ApiAccess])
def api_goals(session: Session = Depends(get_session)):
    return [
        {
            "id": item.id,
            "name": item.name,
            "target_amount": money(item.target_amount),
            "current_amount": money(item.current_amount),
            "monthly_contribution": money(item.monthly_contribution),
            "target_date": item.target_date.isoformat() if item.target_date else None,
        }
        for item in session.scalars(select(Goal).where(Goal.active.is_(True)).order_by(Goal.name)).all()
    ]


@router.get("/subscriptions", dependencies=[ApiAccess])
def api_subscriptions(session: Session = Depends(get_session)):
    return [
        {
            "id": item.id,
            "name": item.name,
            "amount": money(item.amount),
            "billing_day": item.billing_day,
            "card_id": item.card_id,
            "person_id": item.person_id,
        }
        for item in session.scalars(
            select(Subscription).where(Subscription.active.is_(True)).order_by(Subscription.billing_day)
        ).all()
    ]
