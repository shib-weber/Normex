"""Seed the Normex demo database using the production demo seeder.

This entry point intentionally never creates synthetic standard numbers.
Synthetic records are procurement scenarios/evidence only; standards are
restricted to verified BIS/IS metadata in app.services.seed_service.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.db.database import init_db, SessionLocal
from app.services.seed_service import seed_demo

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        seed_demo(db)
    finally:
        db.close()
