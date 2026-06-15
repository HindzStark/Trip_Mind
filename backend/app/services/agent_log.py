import uuid

from sqlalchemy.orm import Session

from app.models.agent_log import AgentLog
from app.schemas.agent_log import AgentLogCreate


def create_log(db: Session, log_data: AgentLogCreate) -> AgentLog:
    log = AgentLog(**log_data.model_dump())

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_logs_by_trip(db: Session, trip_id: uuid.UUID) -> list[AgentLog]:
    return (
        db.query(AgentLog)
        .filter(AgentLog.trip_id == trip_id)
        .order_by(AgentLog.created_at)
        .all()
    )
