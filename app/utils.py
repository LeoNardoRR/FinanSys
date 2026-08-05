from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation


def parse_money(raw: str | Decimal | int | float) -> Decimal:
    if isinstance(raw, Decimal):
        return raw.quantize(Decimal("0.01"))
    text = str(raw).strip().replace("R$", "").replace(" ", "")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("Informe um valor monetário válido.") from exc


def add_months(value: date, months: int) -> date:
    index = value.month - 1 + months
    year, month = value.year + index // 12, index % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def safe_day(year: int, month: int, day: int) -> date:
    return date(year, month, min(max(day, 1), monthrange(year, month)[1]))


def invoice_cycle(reference: date, closing_day: int | None, due_day: int | None) -> dict:
    closing = closing_day or 31
    current_close = safe_day(reference.year, reference.month, closing)
    if reference > current_close:
        cycle_end = add_months(current_close, 1)
    else:
        cycle_end = current_close
    previous_close = add_months(cycle_end, -1)
    cycle_start = previous_close + timedelta(days=1)
    due_month = cycle_end.month if (due_day or 1) > cycle_end.day else add_months(cycle_end, 1).month
    due_year = cycle_end.year if due_month >= cycle_end.month else cycle_end.year + 1
    due = safe_day(due_year, due_month, due_day or 1)
    return {"start": cycle_start, "end": cycle_end, "due": due}



def split_installments(total: Decimal, count: int) -> list[Decimal]:
    if count < 1:
        raise ValueError("A quantidade de parcelas deve ser maior que zero.")
    value = parse_money(total)
    base = (value / count).quantize(Decimal("0.01"))
    amounts = [base for _ in range(count)]
    amounts[-1] = value - sum(amounts[:-1], Decimal(0))
    return amounts
