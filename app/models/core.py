from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(20), default="expense")
    color: Mapped[str] = mapped_column(String(7), default="#6d5dfc")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Bank(Base):
    __tablename__ = "banks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    brand: Mapped[str | None] = mapped_column(String(40), nullable=True)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    closing_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bank_id: Mapped[int | None] = mapped_column(ForeignKey("banks.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    current_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    monthly_contribution: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    billing_day: Mapped[int] = mapped_column(Integer)
    payment_method_id: Mapped[int | None] = mapped_column(ForeignKey("payment_methods.id"), nullable=True)
    card_id: Mapped[int | None] = mapped_column(ForeignKey("cards.id"), nullable=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    last_generated_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
