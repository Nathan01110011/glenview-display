"""Initialisation Point For Backend"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from state_routes import router as state_router
from weather import router as weather_router

app = FastAPI()
app.include_router(state_router)
app.include_router(weather_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("rest_server:app", host="0.0.0.0", port=8000, reload=True)
