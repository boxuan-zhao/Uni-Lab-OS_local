from dataclasses import dataclass, field
from typing import Optional, Any
import time
import uuid


def new_id() -> str:
    return str(uuid.uuid4())


def now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Protocol:
    name: str
    flow_json: str
    description: str = ""
    id: str = field(default_factory=new_id)


@dataclass
class Job:
    protocol_id: Optional[str]
    device_id: str
    action: str
    id: str = field(default_factory=new_id)
    unilab_job_id: Optional[str] = None
    status: int = 1  # 1:submitted 2:running 4:success 5:cancelled 6:aborted
    result: Optional[str] = None


# Job status constants
JOB_STATUS = {
    1: "submitted",
    2: "running",
    4: "success",
    5: "cancelled",
    6: "aborted",
}
