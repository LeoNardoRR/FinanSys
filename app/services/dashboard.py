from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Card, Category, Goal, Person, Subscription, Transaction
from app.utils import invoice_cycle


def _transaction_filters(start: date, end: date, person_id: int | None):
    filters = [Transaction.occurred_on.between(start, end)]
    if person_id:
        filters.append(Transaction.person_id == person_id)
    return filters


def build_dashboard(session: Session, person_id: int | None = None, reference_date: date | None = None) -> dict:
    today = reference_date or date.today()
    start = today.replace(day=1)
    end = today.replace(day=monthrange(today.year, today.month)[1])
    filters = _transaction_filters(start, end, person_id)

    def total(kind: str) -> Decimal:
        value = session.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                *filters, Transaction.kind == kind
            )
        )
        return Decimal(value or 0)

    income, expenses = total("income"), total("expense")
    category_rows = session.execute(
        select(Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(*filters, Transaction.kind == "expense")
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(8)
    ).all()
    recent_query = select(Transaction).where(*filters).order_by(
        Transaction.occurred_on.desc(), Transaction.id.desc()
    ).limit(8)
    monthly_goal = Decimal(
        session.scalar(
            select(func.coalesce(func.sum(Goal.monthly_contribution), 0)).where(Goal.active.is_(True))
        ) or 0
    )
    people_metrics = []
    for person in session.scalars(select(Person).where(Person.active.is_(True)).order_by(Person.name)).all():
        p_filters = _transaction_filters(start, end, person.id)
        p_income = Decimal(session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(*p_filters, Transaction.kind == "income")) or 0)
        p_expense = Decimal(session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(*p_filters, Transaction.kind == "expense")) or 0)
        people_metrics.append({"id": person.id, "name": person.name, "income": p_income, "expenses": p_expense, "balance": p_income - p_expense})

    alerts = []
    for card in session.scalars(select(Card).where(Card.active.is_(True))).all():
        limit = Decimal(card.credit_limit or 0)
        if not limit:
            continue
        cycle = invoice_cycle(today, card.closing_day, card.due_day)
        used = Decimal(session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.card_id == card.id, Transaction.kind == "expense", Transaction.occurred_on.between(cycle["start"], cycle["end"]))) or 0)
        if used / limit >= Decimal("0.85"):
            alerts.append({"level": "warning", "text": f"{card.name}: {used / limit:.0%} do limite utilizado."})
    for subscription in session.scalars(select(Subscription).where(Subscription.active.is_(True))).all():
        if subscription.billing_day in {today.day, today.day + 1}:
            when = "hoje" if subscription.billing_day == today.day else "amanhã"
            alerts.append({"level": "info", "text": f"{subscription.name}: cobrança de R$ {subscription.amount:.2f} {when}."})

    return {
        "income": income, "expenses": expenses, "balance": income - expenses,
        "monthly_goal": monthly_goal,
        "goal_percent": min(float(max(income - expenses, 0) / monthly_goal * 100), 100) if monthly_goal else 0,
        "category_labels": [name for name, _ in category_rows],
        "category_values": [float(value) for _, value in category_rows],
        "recent_transactions": session.scalars(recent_query).all(),
        "people_metrics": people_metrics, "alerts": alerts,
        "month_label": today.strftime("%m/%Y"), "selected_person": person_id,
    }
