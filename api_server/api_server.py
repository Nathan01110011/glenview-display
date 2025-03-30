from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Allow Pi devices to talk to the server from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the shared state
state = {
    "occupied_by": None  # Will be set to a string like "frame1"
}

class DeviceID(BaseModel):
    device_id: str

@app.get("/state")
def get_state():
    return {"occupied_by": state["occupied_by"]}

@app.post("/request")
def request_access(data: DeviceID):
    if state["occupied_by"] is None:
        state["occupied_by"] = data.device_id
        print(f"🔐 Reserved by {data.device_id}")
        return {"status": "reserved"}
    elif state["occupied_by"] == data.device_id:
        return {"status": "already_reserved"}
    else:
        raise HTTPException(status_code=403, detail="Resource already in use")

@app.post("/release")
def release_access(data: DeviceID):
    if state["occupied_by"] == data.device_id:
        state["occupied_by"] = None
        print(f"🔓 Released by {data.device_id}")
        return {"status": "released"}
    else:
        raise HTTPException(status_code=403, detail="You don't hold the lock")

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)
