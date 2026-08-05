from calendar import monthrange
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Card, Category, PaymentMethod, Person, Subscription, Transaction
from app.settings import TEMPLATE_DIR
from app.utils import parse_money

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _subscription_date(year: int, month: int, billing_day: int) -> date:
    return date(year, month, min(billing_day, monthrange(year, month)[1]))


@router.get("", name="subscriptions")
def subscriptions(request: Request, session: Session = Depends(get_session)):
    cards = session.scalars(select(Card).where(Card.active.is_(True)).order_by(Card.name)).all()
    methods = session.scalars(select(PaymentMethod).where(PaymentMethod.active.is_(True)).order_by(PaymentMethod.name)).all()
    people = session.scalars(select(Person).where(Person.active.is_(True)).order_by(Person.name)).all()
    items = session.scalars(select(Subscription).order_by(Subscription.active.desc(), Subscription.billing_day, Subscription.name)).all()
    monthly_total = sum((Decimal(item.amount) for item in items if item.active), Decimal(0))
    names = {item.id: item.name for item in people}
    return templates.TemplateResponse(request, "subscriptions.html", {
        "page_title": "Assinaturas", "subscriptions": items, "cards": cards,
        "payment_methods": methods, "people": people, "person_names": names,
        "monthly_total": monthly_total, "saved": request.query_params.get("saved") == "1",
        "generated": request.query_params.get("generated"), "today": date.today(),
    })


@router.post("", name="create_subscription")
def create_subscription(
    name: str = Form(...), amount: str = Form(...), billing_day: int = Form(...),
    payment_method_id: int | None = Form(None), card_id: int | None = Form(None),
    person_id: int | None = Form(None), session: Session = Depends(get_session),
):
    if not 1 <= billing_day <= 31:
        raise HTTPException(422, "O dia deve estar entre 1 e 31.")
    try:
        value = parse_money(amount)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if not name.strip() or value <= 0:
        raise HTTPException(422, "Informe nome e valor maior que zero.")
    session.add(Subscription(name=name.strip(), amount=value, billing_day=billing_day,
                             payment_method_id=payment_method_id, card_id=card_id, person_id=person_id))
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(422, "Já existe uma assinatura com esse nome.") from exc
    return RedirectResponse("/subscriptions?saved=1", status_code=303)


@router.post("/generate", name="generate_subscriptions")
def generate_subscriptions(
    year: int = Form(...), month: int = Form(...), session: Session = Depends(get_session),
):
    if not 1 <= month <= 12 or not 2000 <= year <= 2200:
        raise HTTPException(422, "Mês ou ano inválido.")
    category = session.scalar(select(Category).where(Category.name == "Assinaturas"))
    if category is None:
        category = Category(name="Assinaturas", kind="expense", color="#7c3aed")
        session.add(category)
        session.flush()
    generated = 0
    for item in session.scalars(select(Subscription).where(Subscription.active.is_(True))).all():
        occurred_on = _subscription_date(year, month, item.billing_day)
        exists = session.scalar(select(Transaction.id).where(
            Transaction.kind == "expense", Transaction.description == item.name,
            Transaction.occurred_on == occurred_on, Transaction.card_id == item.card_id,
        ))
        if exists:
            continue
        session.add(Transaction(occurred_on=occurred_on, description=item.name, amount=item.amount,
                                kind="expense", category_id=category.id,
                                payment_method_id=item.payment_method_id, card_id=item.card_id,
                                person_id=item.person_id, notes="Gerado automaticamente pela assinatura."))
        item.last_generated_on = occurred_on
        generated += 1
    session.commit()
    return RedirectResponse(f"/subscriptions?generated={generated}", status_code=303)


@router.post("/{subscription_id}/toggle", name="toggle_subscription")
def toggle_subscription(subscription_id: int, session: Session = Depends(get_session)):
    item = session.get(Subscription, subscription_id)
    if item is None:
        raise HTTPException(404, "Assinatura não encontrada.")
    item.active = not item.active
    session.commit()
    return RedirectResponse("/subscriptions?saved=1", status_code=303)
