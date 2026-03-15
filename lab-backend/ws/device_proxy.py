"""WebSocket proxy: relay UniLab device-status stream to connected clients."""

from __future__ import annotations
import asyncio
import json
import logging
import os
from typing import Set

import websockets
from fastapi import WebSocket, WebSocketDisconnect

UNILAB_WS = os.environ.get("UNILAB_WS_URL", "ws://localhost:8002/api/v1/ws/device-status")

logger = logging.getLogger("device_proxy")

# All currently connected Node-RED / dashboard clients
_clients: Set[WebSocket] = set()
# Latest snapshot from UniLab (so new clients get data immediately)
_last_payload: str = "{}"


async def _unilab_listener():
    """Persistent connection to UniLab; broadcasts messages to all clients."""
    global _last_payload
    backoff = 2
    while True:
        try:
            async with websockets.connect(UNILAB_WS, ping_interval=20) as ws:
                logger.info(f"Connected to UniLab WS: {UNILAB_WS}")
                backoff = 2
                async for raw in ws:
                    _last_payload = raw
                    dead: list[WebSocket] = []
                    for client in list(_clients):
                        try:
                            await client.send_text(raw)
                        except Exception:
                            dead.append(client)
                    for c in dead:
                        _clients.discard(c)
        except Exception as exc:
            logger.warning(f"UniLab WS disconnected ({exc}), retry in {backoff}s")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


# Background task handle
_listener_task: asyncio.Task | None = None


def start_proxy(app):
    """Register startup/shutdown lifecycle hooks on the FastAPI app."""

    @app.on_event("startup")
    async def _start():
        global _listener_task
        _listener_task = asyncio.create_task(_unilab_listener())

    @app.on_event("shutdown")
    async def _stop():
        if _listener_task:
            _listener_task.cancel()


async def device_status_endpoint(websocket: WebSocket):
    """FastAPI WebSocket endpoint: /ws/device-status"""
    await websocket.accept()
    _clients.add(websocket)
    # Send last known state immediately
    try:
        await websocket.send_text(_last_payload)
    except Exception:
        pass
    try:
        while True:
            # Keep connection alive; actual data is pushed by the listener
            await asyncio.sleep(30)
            await websocket.send_text(_last_payload)
    except (WebSocketDisconnect, Exception):
        _clients.discard(websocket)
