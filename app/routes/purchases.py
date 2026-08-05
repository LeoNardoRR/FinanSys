from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Card, Category, PaymentMethod, Person, PlannedExpense, Purchase, Transaction
from app.settings import TEMPLATE_DIR
from app.utils import add_months, invoice_cycle, parse_money, split_installments

router = APIRouter(prefix="/purchases", tags=["purchases"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _active(session: Session, model):
    return session.scalars(select(model).where(model.active.is_(True)).order_by(model.name)).all()


def _purchase_row(session: Session, purchase: Purchase, cards: dict[int, Card], people: dict[int, str], categories: dict[int, str]) -> dict:
    card = cards.get(purchase.card_id)
    installments = session.scalars(
        select(Transaction).where(Transaction.purchase_id == purchase.id).order_by(Transaction.installment_number)
    ).all()
    today = date.today()
    installment_rows = []
    remaining = Decimal(0)
    elapsed = 0
    next_due = None
    for item in installments:
        due = invoice_cycle(item.occurred_on, card.closing_day if card else None, card.due_day if card else None)["due"]
        if due < today:
            label = "Vencimento passado"
            elapsed += 1
        elif due == today:
            label = "Vence hoje"
            remaining += Decimal(item.amount)
            next_due = next_due or due
        else:
            label = "Futura"
            remaining += Decimal(item.amount)
            next_due = next_due or due
        installment_rows.append({"transaction": item, "due": due, "label": label})
    total_count = len(installments) or purchase.installments_total
    progress = min(elapsed / total_count * 100, 100) if total_count else 0
    return {
        "purchase": purchase,
        "card": card,
        "person": people.get(purchase.person_id, "Família"),
        "category": categories.get(purchase.category_id, "Compras"),
        "installments": installment_rows,
        "installment_value": Decimal(installments[0].amount) if installments else Decimal(0),
        "remaining": remaining,
        "elapsed": elapsed,
        "next_due": next_due,
        "progress": progress,
        "finished": not next_due,
    }


@router.get("", name="purchases")
def purchases(request: Request, query: str = "", planned_id: int | None = None, session: Session = Depends(get_session)):
    statement = select(Purchase).order_by(Purchase.purchased_on.desc(), Purchase.id.desc())
    if query.strip():
        statement = statement.where(Purchase.product_name.ilike(f"%{query.strip()}%"))
    items = session.scalars(statement).all()
    card_items = session.scalars(select(Card).order_by(Card.name)).all()
    people_items = session.scalars(select(Person).order_by(Person.name)).all()
    category_items = session.scalars(select(Category).order_by(Category.name)).all()
    cards = {item.id: item for item in card_items}
    people = {item.id: item.name for item in people_items}
    categories = {item.id: item.name for item in category_items}
    rows = [_purchase_row(session, item, cards, people, categories) for item in items]
    prefill = session.get(PlannedExpense, planned_id) if planned_id else None
    upcoming_total = sum((row["remaining"] for row in rows), Decimal(0))
    total_purchased = sum((Decimal(row["purchase"].total_amount) for row in rows), Decimal(0))
    active_count = sum(1 for row in rows if not row["finished"])
    eligible_cards = [
        item for item in card_items
        if item.active and item.closing_day and item.due_day
    ]
    return templates.TemplateResponse(request, "purchases.html", {
        "page_title": "Compras parceladas", "purchase_rows": rows,
        "cards": [item for item in card_items if item.active],
        "has_eligible_cards": bool(eligible_cards),
        "people": [item for item in people_items if item.active],
        "categories": [item for item in category_items if item.active and item.kind == "expense"],
        "today": date.today().isoformat(), "query": query,
        "upcoming_total": upcoming_total, "total_purchased": total_purchased,
        "active_count": active_count, "prefill": prefill,
        "saved": request.query_params.get("saved") == "1",
        "protected": request.query_params.get("protected") == "1",
    })


@router.post("", name="create_purchase")
def create_purchase(
    product_name: str = Form(...), total_amount: str = Form(...), purchased_on: date = Form(...),
    installments_total: int = Form(...), card_id: int = Form(...), store_name: str = Form(""),
    category_id: int | None = Form(None), person_id: int | None = Form(None),
    warranty_months: int | None = Form(None), notes: str = Form(""),
    planned_expense_id: int | None = Form(None),
    session: Session = Depends(get_session),
):
    name = product_name.strip()
    if not name:
        raise HTTPException(422, "Informe o produto comprado.")
    if not 1 <= installments_total <= 120:
        raise HTTPException(422, "Informe entre 1 e 120 parcelas.")
    if warranty_months is not None and not 0 <= warranty_months <= 240:
        raise HTTPException(422, "A garantia deve ficar entre 0 e 240 meses.")
    try:
        total = parse_money(total_amount)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if total <= 0:
        raise HTTPException(422, "O valor total deve ser maior que zero.")

    card = session.get(Card, card_id)
    if card is None or not card.active:
        raise HTTPException(422, "Selecione um cartão ativo.")
    if not card.closing_day or not card.due_day:
        raise HTTPException(422, "Configure fechamento e vencimento do cartão antes da compra.")

    if category_id is None:
        category = session.scalar(select(Category).where(Category.name == "Compras"))
        category_id = category.id if category else None
    credit = session.scalar(select(PaymentMethod).where(PaymentMethod.name == "Crédito"))
    group = str(uuid4())
    first_due = invoice_cycle(purchased_on, card.closing_day, card.due_day)["due"]
    last_posting = add_months(purchased_on, installments_total - 1)
    last_due = invoice_cycle(last_posting, card.closing_day, card.due_day)["due"]
    warranty_until = add_months(purchased_on, warranty_months) if warranty_months else None

    purchase = Purchase(
        product_name=name, store_name=store_name.strip() or None, total_amount=total,
        purchased_on=purchased_on, installments_total=installments_total, card_id=card.id,
        category_id=category_id, person_id=person_id, first_due_on=first_due,
        last_due_on=last_due, warranty_months=warranty_months or None,
        warranty_until=warranty_until, installment_group=group,
        notes=notes.strip() or None,
    )
    session.add(purchase)
    session.flush()

    for number, amount in enumerate(split_installments(total, installments_total), start=1):
        session.add(Transaction(
            description=f"{name} ({number}/{installments_total})", amount=amount,
            occurred_on=add_months(purchased_on, number - 1), kind="expense",
            category_id=category_id, payment_method_id=credit.id if credit else None,
            card_id=card.id, person_id=person_id, purchase_id=purchase.id,
            installment_number=number, installments_total=installments_total,
            installment_group=group,
            notes=f"Compra parcelada{f' em {store_name.strip()}' if store_name.strip() else ''}. {notes.strip()}".strip(),
        ))
    if planned_expense_id:
        planned = session.get(PlannedExpense, planned_expense_id)
        if planned and planned.status == "planned":
            planned.status = "converted"
    session.commit()
    return RedirectResponse("/purchases?saved=1", 303)


@router.post("/{purchase_id}/delete", name="delete_purchase")
def delete_purchase(purchase_id: int, session: Session = Depends(get_session)):
    purchase = session.get(Purchase, purchase_id)
    if purchase is None:
        raise HTTPException(404, "Compra não encontrada.")
    transactions = session.scalars(select(Transaction).where(Transaction.purchase_id == purchase.id)).all()
    for item in transactions:
        session.delete(item)
    session.delete(purchase)
    session.commit()
    return RedirectResponse("/purchases", 303)
