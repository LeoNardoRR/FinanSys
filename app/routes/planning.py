from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Category, IncomeSource, Person, PlannedExpense, Transaction
from app.settings import TEMPLATE_DIR
from app.utils import add_months, parse_money

router = APIRouter(prefix="/planning", tags=["planning"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@router.get("", name="planning")
def planning(request: Request, session: Session = Depends(get_session)):
    people = session.scalars(select(Person).order_by(Person.active.desc(), Person.name)).all()
    planned = session.scalars(select(PlannedExpense).order_by(PlannedExpense.status, PlannedExpense.expected_on)).all()
    incomes = session.scalars(select(IncomeSource).order_by(IncomeSource.active.desc(), IncomeSource.name)).all()
    names = {person.id: person.name for person in people}
    start = date.today().replace(day=1)
    end = add_months(start, 4)
    future = session.scalars(select(Transaction).where(
        Transaction.kind == "expense", Transaction.occurred_on >= start, Transaction.occurred_on < end
    ).order_by(Transaction.occurred_on, Transaction.id)).all()
    family_income = sum((Decimal(item.expected_amount) for item in incomes if item.active), Decimal(0))
    future_total = sum((Decimal(item.amount) for item in future), Decimal(0))
    planned_total = sum((Decimal(item.amount) for item in planned if item.status == "planned"), Decimal(0))
    return templates.TemplateResponse(request, "planning.html", {
        "page_title": "Planejamento", "people": people, "planned": planned,
        "incomes": incomes, "names": names, "today": date.today().isoformat(),
        "future": future, "family_income": family_income, "future_total": future_total,
        "planned_total": planned_total, "saved": request.query_params.get("saved") == "1",
    })


@router.post("/person", name="create_person")
def create_person(name: str = Form(...), session: Session = Depends(get_session)):
    if not name.strip():
        raise HTTPException(422, "Informe o nome da pessoa.")
    session.add(Person(name=name.strip()))
    return _commit(session)


@router.post("/person/{person_id}/toggle", name="toggle_person")
def toggle_person(person_id: int, session: Session = Depends(get_session)):
    item = session.get(Person, person_id)
    if item is None:
        raise HTTPException(404, "Pessoa não encontrada.")
    item.active = not item.active
    session.commit()
    return RedirectResponse("/planning?saved=1", 303)


@router.post("/income", name="create_income_source")
def create_income_source(
    name: str = Form(...), amount: str = Form(...), person_id: int | None = Form(None),
    session: Session = Depends(get_session),
):
    try:
        value = parse_money(amount)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if not name.strip() or value <= 0:
        raise HTTPException(422, "Informe uma fonte e um valor maior que zero.")
    session.add(IncomeSource(name=name.strip(), expected_amount=value, person_id=person_id))
    session.commit()
    return RedirectResponse("/planning?saved=1", 303)


@router.post("/income/{income_id}/toggle", name="toggle_income_source")
def toggle_income_source(income_id: int, session: Session = Depends(get_session)):
    item = session.get(IncomeSource, income_id)
    if item is None:
        raise HTTPException(404, "Fonte de renda não encontrada.")
    item.active = not item.active
    session.commit()
    return RedirectResponse("/planning?saved=1", 303)


@router.post("/expense", name="create_planned_expense")
def create_planned_expense(
    description: str = Form(...), amount: str = Form(...), expected_on: date = Form(...),
    person_id: int | None = Form(None), session: Session = Depends(get_session),
):
    try:
        value = parse_money(amount)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if not description.strip() or value <= 0:
        raise HTTPException(422, "Informe descrição e valor maior que zero.")
    session.add(PlannedExpense(description=description.strip(), amount=value,
                               expected_on=expected_on, person_id=person_id))
    session.commit()
    return RedirectResponse("/planning?saved=1", 303)


@router.post("/expense/{expense_id}/convert", name="convert_expense")
def convert_expense(
    expense_id: int, category_id: int | None = Form(None), session: Session = Depends(get_session),
):
    item = session.get(PlannedExpense, expense_id)
    if item is None or item.status != "planned":
        raise HTTPException(404, "Gasto previsto não encontrado ou já convertido.")
    session.add(Transaction(description=item.description, amount=item.amount,
                            occurred_on=item.expected_on, kind="expense",
                            person_id=item.person_id, category_id=category_id,
                            notes="Convertido de gasto previsto."))
    item.status = "converted"
    session.commit()
    return RedirectResponse("/transactions?saved=1", 303)


@router.post("/expense/{expense_id}/cancel", name="cancel_planned_expense")
def cancel_planned_expense(expense_id: int, session: Session = Depends(get_session)):
    item = session.get(PlannedExpense, expense_id)
    if item is None:
        raise HTTPException(404, "Gasto previsto não encontrado.")
    item.status = "cancelled"
    session.commit()
    return RedirectResponse("/planning?saved=1", 303)


def _commit(session: Session):
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(422, "Já existe uma pessoa com esse nome.") from exc
    return RedirectResponse("/planning?saved=1", 303)
