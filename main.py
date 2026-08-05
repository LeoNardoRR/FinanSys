from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import initialize_database
from app.routes.cards import router as cards_router
from app.routes.cash_flow import router as cash_flow_router
from app.routes.dashboard import router as dashboard_router
from app.routes.goals import router as goals_router
from app.routes.health import router as health_router
from app.routes.help import router as help_router
from app.routes.planning import router as planning_router
from app.routes.purchases import router as purchases_router
from app.routes.reports import router as reports_router
from app.routes.settings import router as settings_router
from app.routes.subscriptions import router as subscriptions_router
from app.routes.transactions import router as transactions_router
from app.services.automatic_backup import rotate_automatic_backups
from app.settings import APP_NAME, STATIC_DIR

logger = logging.getLogger("finansys")


def _automatic_backup(event: str) -> dict:
    try:
        result = rotate_automatic_backups(event)
        if result.get("success"):
            logger.info("Backup automático criado em %s", result["directory"])
        return result
    except Exception:
        logger.exception("Não foi possível criar o backup automático durante %s.", event)
        return {"success": False, "reason": "unexpected_error", "event": event}


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    app.state.automatic_backup = _automatic_backup("abertura")
    yield
    app.state.automatic_backup = _automatic_backup("encerramento")


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
for router in (
    dashboard_router, transactions_router, purchases_router, cards_router, goals_router,
    subscriptions_router, cash_flow_router, planning_router, settings_router,
    reports_router, help_router, health_router,
):
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
