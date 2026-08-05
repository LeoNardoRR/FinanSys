from datetime import date
from decimal import Decimal
from math import ceil

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Goal
from app.settings import TEMPLATE_DIR
from app.utils import parse_money

router = APIRouter(prefix="/goals", tags=["goals"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def goal_metrics(goal: Goal) -> dict:
    target = Decimal(goal.target_amount)
    current = Decimal(goal.current_amount)
    monthly = Decimal(goal.monthly_contribution or 0)
    remaining = max(target - current, Decimal(0))
    months = ceil(remaining / monthly) if remaining and monthly > 0 else 0
    projected = current + (monthly * 12)
    progress = min(float(current / target * 100), 100) if target else 0
    required_monthly = Decimal(0)
    months_to_deadline = 0
    if goal.target_date and goal.target_date > date.today():
        months_to_deadline = max(
            (goal.target_date.year - date.today().year) * 12 + goal.target_date.month - date.today().month,
            1,
        )
        required_monthly = (remaining / months_to_deadline).quantize(Decimal("0.01"))
    return {
        "goal": goal,
        "remaining": remaining,
        "months": months,
        "projected_12m": projected,
        "progress": progress,
        "required_monthly": required_monthly,
        "months_to_deadline": months_to_deadline,
        "on_track": not required_monthly or monthly >= required_monthly,
    }


@router.get("", name="goals")
def goals(request: Request, session: Session = Depends(get_session)):
    items = session.scalars(select(Goal).order_by(Goal.active.desc(), Goal.target_date.asc(), Goal.name)).all()
    return templates.TemplateResponse(request, "goals.html", {
        "page_title": "Metas",
        "goal_rows": [goal_metrics(item) for item in items],
        "today": date.today().isoformat(),
        "saved": request.query_params.get("saved") == "1",
    })


@router.post("", name="create_goal")
def create_goal(
    name: str = Form(...), target_amount: str = Form(...), current_amount: str = Form("0"),
    monthly_contribution: str = Form("0"), target_date: date | None = Form(None),
    session: Session = Depends(get_session),
):
    try:
        target = parse_money(target_amount)
        current = parse_money(current_amount)
        monthly = parse_money(monthly_contribution)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if not name.strip() or target <= 0 or current < 0 or monthly < 0:
        raise HTTPException(422, "Revise o nome e os valores da meta.")
    session.add(Goal(name=name.strip(), target_amount=target, current_amount=current,
                     monthly_contribution=monthly, target_date=target_date))
    return _commit(session)


@router.post("/{goal_id}/progress", name="update_goal_progress")
def update_goal_progress(
    goal_id: int, current_amount: str = Form(...), monthly_contribution: str = Form(...),
    session: Session = Depends(get_session),
):
    item = session.get(Goal, goal_id)
    if item is None:
        raise HTTPException(404, "Meta não encontrada.")
    try:
        item.current_amount = parse_money(current_amount)
        item.monthly_contribution = parse_money(monthly_contribution)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if item.current_amount < 0 or item.monthly_contribution < 0:
        raise HTTPException(422, "Os valores não podem ser negativos.")
    return _commit(session)


@router.post("/{goal_id}/toggle", name="toggle_goal")
def toggle_goal(goal_id: int, session: Session = Depends(get_session)):
    item = session.get(Goal, goal_id)
    if item is None:
        raise HTTPException(404, "Meta não encontrada.")
    item.active = not item.active
    session.commit()
    return RedirectResponse("/goals?saved=1", status_code=303)


def _commit(session: Session):
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(422, "Já existe uma meta com esse nome.") from exc
    return RedirectResponse("/goals?saved=1", status_code=303)
