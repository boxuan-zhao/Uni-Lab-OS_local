"""Device proxy router – forwards requests to UniLab."""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from lib import unilab_client

router = APIRouter()


@router.get("")
async def list_devices():
    try:
        return await unilab_client.get_online_devices()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"UniLab unreachable: {exc}")


@router.get("/{device_id}/actions")
async def get_device_actions(device_id: str):
    try:
        return await unilab_client.get_device_actions(device_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"UniLab unreachable: {exc}")


@router.get("/{device_id}/actions/{action_name}/schema")
async def get_action_schema(device_id: str, action_name: str):
    try:
        return await unilab_client.get_action_schema(device_id, action_name)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"UniLab unreachable: {exc}")
