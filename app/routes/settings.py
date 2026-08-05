from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Bank, Card, Category, PaymentMethod
from app.settings import TEMPLATE_DIR
from app.services.automatic_backup import BACKUP_1, BACKUP_2, automatic_backup_directory
from app.utils import parse_money

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _items(session: Session, model):
    return session.scalars(select(model).order_by(model.active.desc(), model.name)).all()


@router.get("", name="settings")
def settings(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse(request, "settings.html", {
        "page_title": "Configurações", "categories": _items(session, Category),
        "banks": _items(session, Bank), "payment_methods": _items(session, PaymentMethod),
        "cards": _items(session, Card), "saved": request.query_params.get("saved") == "1",
        "backup": request.query_params.get("backup"), "restored": request.query_params.get("restored"),
        "automatic_backup": getattr(request.app.state, "automatic_backup", {}),
        "automatic_backup_dir": str(automatic_backup_directory()),
        "automatic_backup_files": (BACKUP_1, BACKUP_2),
    })


@router.post("/category", name="create_category")
def create_category(name: str = Form(...), kind: str = Form(...), color: str = Form("#2563eb"), session: Session = Depends(get_session)):
    if kind not in {"income", "expense"}:
        raise HTTPException(422, "Tipo inválido.")
    session.add(Category(name=name.strip(), kind=kind, color=color))
    return _commit(session)


@router.post("/bank", name="create_bank")
def create_bank(name: str = Form(...), session: Session = Depends(get_session)):
    session.add(Bank(name=name.strip()))
    return _commit(session)


@router.post("/payment-method", name="create_payment_method")
def create_payment_method(name: str = Form(...), session: Session = Depends(get_session)):
    session.add(PaymentMethod(name=name.strip()))
    return _commit(session)


@router.post("/card", name="create_card")
def create_card(
    name: str = Form(...), brand: str = Form(""), credit_limit: str = Form("0"),
    closing_day: int | None = Form(None), due_day: int | None = Form(None),
    bank_id: int | None = Form(None), session: Session = Depends(get_session),
):
    try:
        limit = parse_money(credit_limit)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if limit < 0 or (closing_day and not 1 <= closing_day <= 31) or (due_day and not 1 <= due_day <= 31):
        raise HTTPException(422, "Revise limite, fechamento e vencimento.")
    session.add(Card(name=name.strip(), brand=brand.strip() or None, credit_limit=limit,
                     closing_day=closing_day, due_day=due_day, bank_id=bank_id))
    return _commit(session)


@router.post("/{model_name}/{item_id}/toggle", name="toggle_setting")
def toggle_setting(model_name: str, item_id: int, session: Session = Depends(get_session)):
    models = {"category": Category, "bank": Bank, "payment": PaymentMethod, "card": Card}
    model = models.get(model_name)
    if model is None:
        raise HTTPException(404, "Tipo de configuração inválido.")
    item = session.get(model, item_id)
    if item is None:
        raise HTTPException(404, "Item não encontrado.")
    item.active = not item.active
    session.commit()
    return RedirectResponse("/settings?saved=1", 303)


def _commit(session: Session):
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(422, "Já existe um item com esse nome.") from exc
    return RedirectResponse("/settings?saved=1", 303)
