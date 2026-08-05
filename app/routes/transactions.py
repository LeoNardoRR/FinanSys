from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Bank, Card, Category, PaymentMethod, Person, Transaction
from app.settings import TEMPLATE_DIR
from app.utils import add_months, parse_money

router = APIRouter(prefix="/transactions", tags=["transactions"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def active_items(session: Session, model):
    return session.scalars(select(model).where(model.active.is_(True)).order_by(model.name)).all()


def form_options(session: Session) -> dict:
    return {
        "categories": active_items(session, Category),
        "banks": active_items(session, Bank),
        "cards": active_items(session, Card),
        "payment_methods": active_items(session, PaymentMethod),
        "people": active_items(session, Person),
    }


@router.get("", name="transactions")
def transaction_list(request: Request, query: str = "", kind: str = "", person_id: int | None = None, session: Session = Depends(get_session)):
    statement = select(Transaction).order_by(Transaction.occurred_on.desc(), Transaction.id.desc())
    if query.strip():
        statement = statement.where(Transaction.description.ilike(f"%{query.strip()}%"))
    if kind in {"income", "expense"}:
        statement = statement.where(Transaction.kind == kind)
    if person_id:
        statement = statement.where(Transaction.person_id == person_id)
    rows = session.scalars(statement).all()
    context = {
        "page_title": "Lançamentos", "transactions": rows,
        "category_names": {x.id: x.name for x in session.scalars(select(Category)).all()},
        "bank_names": {x.id: x.name for x in session.scalars(select(Bank)).all()},
        "person_names": {x.id: x.name for x in session.scalars(select(Person)).all()},
        "query": query, "kind": kind, "person_id": person_id,
        "today": date.today().isoformat(), "saved": request.query_params.get("saved") == "1",
    }
    context.update(form_options(session))
    return templates.TemplateResponse(request, "transactions.html", context)


@router.post("", name="create_transaction")
def create_transaction(
    description: str = Form(...), amount: str = Form(...), occurred_on: date = Form(...),
    kind: str = Form(...), category_id: int | None = Form(None), bank_id: int | None = Form(None),
    payment_method_id: int | None = Form(None), card_id: int | None = Form(None),
    person_id: int | None = Form(None), installments_total: int = Form(1),
    notes: str | None = Form(None), session: Session = Depends(get_session),
):
    if kind not in {"income", "expense"}:
        raise HTTPException(422, "Tipo inválido.")
    if not 1 <= installments_total <= 120:
        raise HTTPException(422, "Informe entre 1 e 120 parcelas.")
    try:
        total = parse_money(amount)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if total <= 0:
        raise HTTPException(422, "O valor deve ser maior que zero.")

    group = str(uuid4()) if installments_total > 1 else None
    base_value = (total / installments_total).quantize(Decimal("0.01"))
    distributed = Decimal(0)
    for number in range(1, installments_total + 1):
        value = total - distributed if number == installments_total else base_value
        distributed += value
        suffix = f" ({number}/{installments_total})" if installments_total > 1 else ""
        session.add(Transaction(
            description=description.strip() + suffix, amount=value,
            occurred_on=add_months(occurred_on, number - 1), kind=kind,
            category_id=category_id, bank_id=bank_id, payment_method_id=payment_method_id,
            card_id=card_id, person_id=person_id,
            installment_number=number if group else None,
            installments_total=installments_total if group else None,
            installment_group=group, notes=notes.strip() if notes else None,
        ))
    session.commit()
    return RedirectResponse("/transactions?saved=1", 303)


@router.get("/{transaction_id}/edit", name="edit_transaction")
def edit_transaction(transaction_id: int, request: Request, session: Session = Depends(get_session)):
    item = session.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(404, "Lançamento não encontrado.")
    context = {"page_title": "Editar lançamento", "item": item}
    context.update(form_options(session))
    return templates.TemplateResponse(request, "edit_transaction.html", context)


@router.post("/{transaction_id}/edit", name="save_transaction")
def save_transaction(
    transaction_id: int, description: str = Form(...), amount: str = Form(...),
    occurred_on: date = Form(...), kind: str = Form(...), category_id: int | None = Form(None),
    bank_id: int | None = Form(None), payment_method_id: int | None = Form(None),
    card_id: int | None = Form(None), person_id: int | None = Form(None),
    notes: str | None = Form(None), session: Session = Depends(get_session),
):
    item = session.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(404, "Lançamento não encontrado.")
    try:
        value = parse_money(amount)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if value <= 0 or kind not in {"income", "expense"}:
        raise HTTPException(422, "Dados inválidos.")
    item.description, item.amount, item.occurred_on, item.kind = description.strip(), value, occurred_on, kind
    item.category_id, item.bank_id, item.payment_method_id = category_id, bank_id, payment_method_id
    item.card_id, item.person_id, item.notes = card_id, person_id, notes.strip() if notes else None
    session.commit()
    return RedirectResponse("/transactions?saved=1", 303)


@router.post("/{transaction_id}/delete", name="delete_transaction")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    item = session.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(404, "Lançamento não encontrado.")
    if item.purchase_id:
        return RedirectResponse("/purchases?protected=1", 303)
    session.delete(item)
    session.commit()
    return RedirectResponse("/transactions", 303)
