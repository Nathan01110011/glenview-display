from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory state
state: dict[str, Optional[str]] = {
    "occupied_by": None,
    "start_time": None
}

class DeviceAction(BaseModel):
    device_id: str

@router.get("/state")
def get_state():
    return state

@router.post("/request")
def reserve(action: DeviceAction):
    if state["occupied_by"] is None:
        state["occupied_by"] = action.device_id
        state["start_time"] = datetime.now(timezone.utc).isoformat()
    return state

@router.post("/release")
def release(action: DeviceAction):
    if state["occupied_by"] == action.device_id:
        state["occupied_by"] = None
    return state
