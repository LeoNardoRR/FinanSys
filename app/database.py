from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.settings import DATA_DIR, DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session():
    with SessionLocal() as session:
        yield session


def _add_column(connection, table: str, column: str, definition: str) -> None:
    columns = [row[1] for row in connection.exec_driver_sql(f"PRAGMA table_info({table})")]
    if column not in columns:
        connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    from app.models import all_models  # noqa: F401
    from app.services.seed import seed_defaults

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        _add_column(connection, "goals", "monthly_contribution", "NUMERIC(12, 2) NOT NULL DEFAULT 0")
        _add_column(connection, "transactions", "person_id", "INTEGER")
        _add_column(connection, "transactions", "installment_group", "VARCHAR(36)")
        _add_column(connection, "transactions", "purchase_id", "INTEGER")
        _add_column(connection, "subscriptions", "person_id", "INTEGER")
        _add_column(connection, "subscriptions", "last_generated_on", "DATE")

    with SessionLocal() as session:
        seed_defaults(session)
