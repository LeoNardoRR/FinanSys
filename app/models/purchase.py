from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(160), index=True)
    store_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    purchased_on: Mapped[date] = mapped_column(Date, index=True)
    installments_total: Mapped[int] = mapped_column(Integer)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    first_due_on: Mapped[date] = mapped_column(Date)
    last_due_on: Mapped[date] = mapped_column(Date)
    warranty_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    installment_group: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
