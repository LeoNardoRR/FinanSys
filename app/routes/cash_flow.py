from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Person, Subscription, Transaction
from app.settings import TEMPLATE_DIR
from app.utils import add_months

router = APIRouter(prefix="/cash-flow", tags=["cash-flow"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@router.get("", name="cash_flow")
def cash_flow(
    request: Request, person_id: int | None = Query(None), months: int = Query(6, ge=1, le=36),
    session: Session = Depends(get_session),
):
    start = date.today().replace(day=1)
    end = add_months(start, months)
    query = select(Transaction).where(Transaction.occurred_on < end).order_by(Transaction.occurred_on, Transaction.id)
    if person_id:
        query = query.where(Transaction.person_id == person_id)
    items = session.scalars(query).all()
    balance = Decimal(0)
    rows = []
    monthly = {}
    for item in items:
        signed = Decimal(item.amount) if item.kind == "income" else -Decimal(item.amount)
        balance += signed
        if item.occurred_on >= start:
            rows.append({"item": item, "signed": signed, "balance": balance})
            key = item.occurred_on.strftime("%Y-%m")
            data = monthly.setdefault(key, {"income": Decimal(0), "expense": Decimal(0)})
            data[item.kind] += Decimal(item.amount)
    people = session.scalars(select(Person).where(Person.active.is_(True)).order_by(Person.name)).all()
    subscriptions = session.scalars(select(Subscription).where(Subscription.active.is_(True)).order_by(Subscription.billing_day)).all()
    return templates.TemplateResponse(request, "cash_flow.html", {
        "page_title": "Fluxo de caixa", "rows": rows, "monthly": monthly,
        "people": people, "selected_person": person_id, "months": months,
        "subscriptions": subscriptions, "opening_balance": balance - sum((row["signed"] for row in rows), Decimal(0)),
    })
