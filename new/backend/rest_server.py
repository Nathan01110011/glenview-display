from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Allow any device on LAN to access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to just your Pi subnet if you like
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory state
state = {"occupied_by": None}


class DeviceAction(BaseModel):
    device_id: str


@app.get("/state")
async def get_state():
    return state


@app.post("/request")
async def reserve(action: DeviceAction):
    if state["occupied_by"] is None:
        state["occupied_by"] = action.device_id
    return state


@app.post("/release")
async def release(action: DeviceAction):
    if state["occupied_by"] == action.device_id:
        state["occupied_by"] = None
    return state


if __name__ == "__main__":
    uvicorn.run("rest_server:app", host="0.0.0.0", port=8000, reload=True)
