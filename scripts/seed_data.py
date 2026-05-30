#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import SessionLocal, init_db
from datetime import datetime


def seed():
    init_db()
    session = SessionLocal()
    print("Seeding complete")


if __name__ == "__main__":
    seed()
