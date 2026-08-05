from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Bank, Card, Transaction
from app.settings import TEMPLATE_DIR
from app.utils import invoice_cycle

router = APIRouter(prefix="/cards", tags=["cards"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@router.get("", name="cards")
def cards(request: Request, session: Session = Depends(get_session)):
    today = date.today()
    banks = {item.id: item.name for item in session.scalars(select(Bank)).all()}
    result = []
    for card in session.scalars(select(Card).order_by(Card.active.desc(), Card.name)).all():
        cycle = invoice_cycle(today, card.closing_day, card.due_day)
        purchases = session.scalars(
            select(Transaction).where(
                Transaction.card_id == card.id,
                Transaction.kind == "expense",
                Transaction.occurred_on.between(cycle["start"], cycle["end"]),
            ).order_by(Transaction.occurred_on.desc())
        ).all()
        used = sum((Decimal(item.amount) for item in purchases), Decimal(0))
        limit = Decimal(card.credit_limit or 0)
        result.append({
            "card": card, "bank": banks.get(card.bank_id, "Banco não informado"),
            "used": used, "available": limit - used,
            "percent": min(float(used / limit * 100), 100) if limit else 0,
            "cycle": cycle, "purchases": purchases,
        })
    return templates.TemplateResponse(request, "cards.html", {
        "page_title": "Cartões", "cards": result,
    })
