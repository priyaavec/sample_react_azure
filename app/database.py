import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


azure_sql = os.getenv("AZURE_SQL_CONNECTION_STRING")


if azure_sql:

    connection_url = (
        f"mssql+pyodbc:///?odbc_connect="
        f"{quote_plus(azure_sql)}"
    )

    engine = create_engine(
        connection_url,
        pool_pre_ping=True
    )

else:

    engine = create_engine(
        "sqlite:///./local.db",
        connect_args={
            "check_same_thread": False
        }
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
