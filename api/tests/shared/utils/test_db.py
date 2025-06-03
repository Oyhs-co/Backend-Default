from api.shared.utils.db import get_db
from sqlalchemy.orm import Session

def test_get_db_returns_session() -> None:
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    # Clean up
    try:
        next(gen)
    except StopIteration:
        pass 