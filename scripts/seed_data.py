#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import SessionLocal, init_db
from backend.models.agent import AgentModel
from backend.models.task import TaskModel
from datetime import datetime, timedelta
import uuid


def seed():
    init_db()
    session = SessionLocal()
    try:
        existing = session.query(AgentModel).count()
        if existing > 0:
            print(f"Database already seeded ({existing} agents found), skipping.")
            return

        agent = AgentModel(
            id=str(uuid.uuid4()),
            name="Default Agent",
            llm_provider="openai",
            config={"max_steps": 20, "temperature": 0.7},
            status="idle",
        )
        session.add(agent)

        sample_tasks = [
            TaskModel(
                id=str(uuid.uuid4()),
                title="Research latest AI trends",
                description="Search the web for the latest developments in AI and machine learning",
                priority="high",
                status="completed",
                created_at=datetime.now() - timedelta(days=2),
            ),
            TaskModel(
                id=str(uuid.uuid4()),
                title="Analyze project data",
                description="Run data analysis on the provided dataset and generate insights",
                priority="medium",
                status="pending",
                created_at=datetime.now() - timedelta(days=1),
            ),
            TaskModel(
                id=str(uuid.uuid4()),
                title="Automate report generation",
                description="Create an automated workflow for generating weekly reports",
                priority="low",
                status="pending",
            ),
        ]
        for task in sample_tasks:
            session.add(task)

        session.commit()
        print(f"Seeded {1 + len(sample_tasks)} records: 1 agent, {len(sample_tasks)} tasks")
    except Exception as e:
        session.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        session.close()
    print("Seeding complete")


if __name__ == "__main__":
    seed()
