"""Protocol CRUD router."""

from __future__ import annotations
import json
import uuid
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db

router = APIRouter()


class ProtocolCreate(BaseModel):
    name: str
    description: str = ""
    flow_json: str  # raw Node-RED flow JSON string


class ProtocolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    flow_json: Optional[str] = None


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


@router.get("")
async def list_protocols(db=Depends(get_db)):
    async with db.execute(
        "SELECT id, name, description, created_at, updated_at FROM protocols ORDER BY updated_at DESC"
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
async def create_protocol(body: ProtocolCreate, db=Depends(get_db)):
    pid = str(uuid.uuid4())
    now = _now()
    await db.execute(
        "INSERT INTO protocols (id, name, description, flow_json, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (pid, body.name, body.description, body.flow_json, now, now),
    )
    await db.commit()
    return {"id": pid, "name": body.name, "description": body.description, "created_at": now}


@router.get("/{protocol_id}")
async def get_protocol(protocol_id: str, db=Depends(get_db)):
    async with db.execute("SELECT * FROM protocols WHERE id=?", (protocol_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return dict(row)


@router.put("/{protocol_id}")
async def update_protocol(protocol_id: str, body: ProtocolUpdate, db=Depends(get_db)):
    async with db.execute("SELECT * FROM protocols WHERE id=?", (protocol_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Protocol not found")

    data = dict(row)
    if body.name is not None:
        data["name"] = body.name
    if body.description is not None:
        data["description"] = body.description
    if body.flow_json is not None:
        data["flow_json"] = body.flow_json
    data["updated_at"] = _now()

    await db.execute(
        "UPDATE protocols SET name=?, description=?, flow_json=?, updated_at=? WHERE id=?",
        (data["name"], data["description"], data["flow_json"], data["updated_at"], protocol_id),
    )
    await db.commit()
    return data


@router.delete("/{protocol_id}", status_code=204)
async def delete_protocol(protocol_id: str, db=Depends(get_db)):
    async with db.execute("SELECT id FROM protocols WHERE id=?", (protocol_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Protocol not found")
    await db.execute("DELETE FROM protocols WHERE id=?", (protocol_id,))
    await db.commit()
