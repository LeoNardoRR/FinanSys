from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Bank, Category, PaymentMethod

def seed_defaults(session: Session) -> None:
    defaults = (
        (Category, "name", [{"name":"Salários","kind":"income","color":"#2fb344"},{"name":"Restaurante","kind":"expense","color":"#f76707"},{"name":"Saúde","kind":"expense","color":"#d6336c"},{"name":"Combustível","kind":"expense","color":"#206bc4"},{"name":"Casamento","kind":"expense","color":"#ae3ec9"},{"name":"Investimentos","kind":"expense","color":"#0ca678"},{"name":"Lazer","kind":"expense","color":"#f59f00"},{"name":"Presentes","kind":"expense","color":"#e64980"},{"name":"Compras","kind":"expense","color":"#7c3aed"}]),
        (Bank, "name", [{"name":n} for n in ("Nubank","Mercado Pago","Bradesco")]),
        (PaymentMethod, "name", [{"name":n} for n in ("PIX","Débito","Crédito")]),
    )
    for model, field, entries in defaults:
        for entry in entries:
            if session.scalar(select(model).where(getattr(model, field) == entry[field])) is None:
                session.add(model(**entry))
    session.commit()
