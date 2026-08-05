from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Person
from app.services.dashboard import build_dashboard
from app.settings import TEMPLATE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@router.get("/", name="dashboard")
def dashboard(request: Request, person_id: int | None = None, session: Session = Depends(get_session)):
    people = session.scalars(select(Person).where(Person.active.is_(True)).order_by(Person.name)).all()
    return templates.TemplateResponse(request, "dashboard.html", {
        "page_title": "Dashboard",
        "dashboard": build_dashboard(session, person_id=person_id),
        "people": people,
        "selected_person": person_id,
    })
