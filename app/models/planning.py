from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class IncomeSource(Base):
    __tablename__ = "income_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class PlannedExpense(Base):
    __tablename__ = "planned_expenses"
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(160))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    expected_on: Mapped[date] = mapped_column(Date)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planned")
