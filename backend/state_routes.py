from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory state
state = {"occupied_by": None}

class DeviceAction(BaseModel):
    device_id: str

@router.get("/state")
def get_state():
    return state

@router.post("/request")
def reserve(action: DeviceAction):
    if state["occupied_by"] is None:
        state["occupied_by"] = action.device_id
    return state

@router.post("/release")
def release(action: DeviceAction):
    if state["occupied_by"] == action.device_id:
        state["occupied_by"] = None
    return state
