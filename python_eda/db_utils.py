# Shared PostgreSQL connection helper for EDA scripts.

import os
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_engine():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "deal_hopper")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    if not password or password == "your_postgres_password_here":
        raise RuntimeError(
            "Database password not set. Copy .env.example to .env in the "
            "project root and fill in your real Postgres password before "
            "running EDA scripts."
        )

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)
