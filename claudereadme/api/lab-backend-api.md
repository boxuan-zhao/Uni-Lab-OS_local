# UniLab Local Node-RED System

## Architecture

```
Node-RED (localhost:1880)
    ↕ HTTP REST
lab-backend (localhost:3000)   ← FastAPI + SQLite
    ↕ HTTP + WebSocket
UniLab (localhost:8002)        ← ROS2 backend
    ↕ device protocols
Lab equipment
```

## Quick Start

### 1. Start UniLab in local mode
```bash
mamba activate unilab
unilab --local_mode \
       --backend ros \
       --app_bridges fastapi \
       -g devices_graph.json \
       --upload_registry false
```

### 2. Start the backend
```bash
cd lab-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### 3. Install Node-RED nodes
```bash
cd ~/.node-red
npm install /path/to/node-red-contrib-unilab
node-red
```

## lab-backend API

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/protocols | List protocols |
| POST | /api/protocols | Create protocol (save Node-RED flow JSON) |
| GET | /api/protocols/{id} | Get protocol detail |
| PUT | /api/protocols/{id} | Update protocol |
| DELETE | /api/protocols/{id} | Delete protocol |
| POST | /api/jobs/submit | Submit protocol as UniLab jobs |
| POST | /api/jobs/submit-single | Submit a single ad-hoc job |
| GET | /api/jobs/{id}/status | Query job status (syncs with UniLab) |
| GET | /api/jobs | List recent jobs |
| GET | /api/devices | List online devices (proxy) |
| GET | /api/devices/{id}/actions | Device actions (proxy) |
| GET | /api/devices/{id}/actions/{name}/schema | Action schema (proxy) |
| WS | /ws/device-status | Real-time device status stream |
| GET | /health | Health check |

## Node-RED Nodes

**Category: UniLab**
- `unilab-config` — Backend URL configuration (config node)
- `unilab-device-list` — Fetch online devices
- `unilab-submit-job` — Submit a protocol for execution
- `unilab-job-status` — Poll job status until completion (2 outputs: success / failure)
- `unilab-device-monitor` — WebSocket device status stream (0 inputs, 1 output)

**Category: UniLab操作**
- `unilab-transfer-liquid` — Liquid transfer
- `unilab-incubation` — Incubation
- `unilab-heat-chill` — Temperature control
- `unilab-move-labware` — Labware movement

Each operation node has two modes:
- **立即执行**: Submits immediately as a single job
- **协议描述符**: Passes `msg.payload` descriptor downstream (for protocol flows)

## Flow → Protocol → Execution

1. Design protocol in Node-RED using UniLab operation nodes
2. Save the flow JSON via `POST /api/protocols`
3. Trigger execution via `unilab-submit-job` node or `POST /api/jobs/submit`
4. The backend converter (`lib/converter.py`) topologically sorts nodes and maps them to UniLab jobs
5. Monitor via `unilab-device-monitor` + Node-RED Dashboard
