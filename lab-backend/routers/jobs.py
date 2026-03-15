"""Job management router."""

from __future__ import annotations
import json
import uuid
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from lib.converter import convert_flow_to_jobs
from lib import unilab_client

router = APIRouter()


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


class JobSubmit(BaseModel):
    protocol_id: str


class SingleJobSubmit(BaseModel):
    device_id: str
    action: str
    action_args: dict = {}


@router.post("/submit", status_code=201)
async def submit_protocol_jobs(body: JobSubmit, db=Depends(get_db)):
    """Convert a protocol's Node-RED flow to UniLab jobs and submit them."""
    async with db.execute("SELECT * FROM protocols WHERE id=?", (body.protocol_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Protocol not found")

    protocol = dict(row)
    flow_nodes: list = json.loads(protocol["flow_json"])
    job_defs = convert_flow_to_jobs(flow_nodes)

    if not job_defs:
        raise HTTPException(status_code=422, detail="No executable UniLab nodes found in flow")

    submitted: list[dict] = []
    for jd in job_defs:
        try:
            resp = await unilab_client.submit_job(jd["device_id"], jd["action"], jd["action_args"])
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"UniLab error: {exc}")

        unilab_job_id = resp.get("data", {}).get("id") or resp.get("id")
        jid = str(uuid.uuid4())
        now = _now()
        await db.execute(
            "INSERT INTO jobs (id, protocol_id, unilab_job_id, device_id, action, status, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (jid, body.protocol_id, unilab_job_id, jd["device_id"], jd["action"], 1, now),
        )
        submitted.append({"id": jid, "unilab_job_id": unilab_job_id, "device_id": jd["device_id"], "action": jd["action"]})

    await db.commit()
    return {"protocol_id": body.protocol_id, "jobs": submitted}


@router.post("/submit-single", status_code=201)
async def submit_single_job(body: SingleJobSubmit, db=Depends(get_db)):
    """Submit a single ad-hoc job directly to UniLab."""
    try:
        resp = await unilab_client.submit_job(body.device_id, body.action, body.action_args)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"UniLab error: {exc}")

    unilab_job_id = resp.get("data", {}).get("id") or resp.get("id")
    jid = str(uuid.uuid4())
    now = _now()
    await db.execute(
        "INSERT INTO jobs (id, protocol_id, unilab_job_id, device_id, action, status, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (jid, None, unilab_job_id, body.device_id, body.action, 1, now),
    )
    await db.commit()
    return {"id": jid, "unilab_job_id": unilab_job_id}


@router.get("/{job_id}/status")
async def get_job_status(job_id: str, db=Depends(get_db)):
    """Query job status (syncs with UniLab)."""
    async with db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job = dict(row)
    if job.get("unilab_job_id"):
        try:
            unilab_status = await unilab_client.get_job_status(job["unilab_job_id"])
            new_status = unilab_status.get("data", {}).get("status", job["status"])
            result = json.dumps(unilab_status.get("data", {}))
            if new_status != job["status"]:
                await db.execute(
                    "UPDATE jobs SET status=?, result=? WHERE id=?",
                    (new_status, result, job_id),
                )
                await db.commit()
            job["status"] = new_status
            job["unilab_data"] = unilab_status.get("data")
        except Exception:
            pass  # Return cached status if UniLab is unreachable

    return job


@router.get("")
async def list_jobs(db=Depends(get_db)):
    async with db.execute(
        "SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100"
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]
