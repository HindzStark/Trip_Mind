import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AgentLogCreate(BaseModel):
    trip_id: uuid.UUID
    agent_name: str
    input_json: str | None = None
    output_json: str | None = None
    execution_time_ms: int | None = None


class AgentLogResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    agent_name: str
    input_json: str | None
    output_json: str | None
    execution_time_ms: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
