"""
DB engine & session management (SQLModel + pooling).
"""

import os
import logging
from typing import Generator, Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, text

# -----------------------------------------------------------------------------
# Load environment & basic logging
# -----------------------------------------------------------------------------
load_dotenv(override=True)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Build connection URL directly from .env
# -----------------------------------------------------------------------------
SB_USER = os.getenv("SB_USER", "")
SB_PASSWORD = os.getenv("SB_PASSWORD", "")
SB_HOST = os.getenv("SB_HOST", "")
SB_PORT = os.getenv("SB_PORT", "5432")
SB_DBNAME = os.getenv("SB_DBNAME", "")

if not all([SB_USER, SB_PASSWORD, SB_HOST, SB_DBNAME]):
    raise RuntimeError("Missing database configuration in .env")

# URL-encode password to handle special characters like @ in passwords
encoded_password = quote_plus(SB_PASSWORD)
DATABASE_URL = f"postgresql://{SB_USER}:{encoded_password}@{SB_HOST}:{SB_PORT}/{SB_DBNAME}"

# -----------------------------------------------------------------------------
# SQLModel Engine & Session
# -----------------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=os.getenv("SQL_ECHO", "0") == "1",
)

def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session (context-managed)."""
    with Session(engine) as session:
        yield session

def new_session() -> Session:
    """Return a SQLModel session (caller closes/commits)."""
    return Session(engine)

def check_connection() -> bool:
    """Return True if DB connection works."""
    try:
        with Session(engine) as session:
            session.exec(select(1))  # type: ignore
        return True
    except Exception as e:
        logger.error(f"DB connection check failed: {e}")
        return False