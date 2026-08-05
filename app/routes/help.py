from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.settings import TEMPLATE_DIR

router = APIRouter(tags=["help"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@router.get("/help", name="help_page")
def help_page(request: Request):
    return templates.TemplateResponse(request, "help.html", {"page_title": "Como usar"})
