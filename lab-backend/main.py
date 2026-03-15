"""
UniLab Local Backend
====================
FastAPI middleware between Node-RED and UniLab (localhost:8002).

Start with:
    uvicorn main:app --host 0.0.0.0 --port 3000 --reload

Environment variables:
    UNILAB_URL      UniLab HTTP base URL  (default: http://localhost:8002)
    UNILAB_WS_URL   UniLab WebSocket URL  (default: ws://localhost:8002/api/v1/ws/device-status)
    LAB_DB_PATH     SQLite database path  (default: lab.db)
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import protocols, jobs, devices
from ws.device_proxy import device_status_endpoint, start_proxy


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="UniLab Local Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routers
app.include_router(protocols.router, prefix="/api/protocols", tags=["Protocols"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])

# WebSocket proxy
start_proxy(app)


@app.websocket("/ws/device-status")
async def ws_device_status(websocket: WebSocket):
    await device_status_endpoint(websocket)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
