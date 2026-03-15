# UniLab-OS 探索指南与系统架构文档

> **目标读者**：需要理解 UniLab-OS 架构、扩展功能或集成新设备的开发者/Agent

---

## 📋 目录

1. [项目概述](#项目概述)
2. [已导出的文档](#已导出的文档)
3. [核心架构](#核心架构)
4. [关键文件索引](#关键文件索引)
5. [探索方法论](#探索方法论)
6. [常见任务指南](#常见任务指南)
7. [扩展开发指南](#扩展开发指南)

---

## 项目概述

### 基本信息
- **项目路径**：`C:\Users\21082\PycharmProjects\Uni-Lab-OS`
- **核心技术栈**：Python 3.x + ROS2 + FastAPI + PyLabRobot
- **平台**：Windows 11 (bash shell, 使用 Unix 路径)
- **用途**：实验室自动化平台，支持液体处理、温控、机械臂、分析仪器等设备的统一控制

### 系统组成
```
UniLab-OS/
├── unilabos/                    # 核心库
│   ├── app/                     # 应用层（CLI、Web服务）
│   ├── devices/                 # 设备驱动（31+ 种设备类型）
│   ├── workflow/                # 工作流编译器
│   ├── registry/                # 设备注册表（YAML配置）
│   ├── resources/               # 资源管理（设备连接图）
│   ├── ros/                     # ROS2 节点
│   └── config/                  # 配置管理
├── lab-backend/                 # FastAPI 中间层（新增）
└── node-red-contrib-unilab/     # Node-RED 自定义节点（新增）
```

---

## 已导出的文档

### 1. `UNILAB_COMPILATION_ANALYSIS.md`
**内容**：UniLab 编译转化机制深度分析
- **三层编译架构**：化学协议 → 设备操作 → 硬件指令
- **设备连接图的作用**：每一层编译如何使用 `devices_graph.json`
- **完整编译链路示例**：从 XDL 到泵阀指令的全过程
- **代��位置**：关键编译函数的文件路径和行号

**适用场景**：
- 理解 UniLab 如何将高级化学指令编译为底层硬件操作
- 开发新的工作流编译器
- 调试编译错误

### 2. `UNILAB_SUPPORTED_OPERATIONS.md`
**内容**：UniLab 内核支持的所有编译操作清单
- **7 大类操作**：液体处理、温控、机械臂、泵阀、分析仪器、有机合成、工作站
- **每个操作的参数说明**：输入参数、编译层级、生成指令数
- **编译示例**：输入 → 中间表示 → 硬件指令
- **操作复杂度对比**：哪些操作依赖设备连接图

**适用场景**：
- 查询 UniLab 是否支持某个操作
- 了解操作的参数格式
- 评估新操作的开发难度

### 3. `lab-backend/README.md`
**内容**：FastAPI 中间层架构说明
- **API 端点列表**：协议管理、任务管理、设备代理、WebSocket
- **数据库设计**：SQLite 表结构
- **格式转换器**：Node-RED flow → UniLab job
- **启动命令**：如何运行 backend

**适用场景**：
- 集成 Node-RED 与 UniLab
- 开发 Web 前端
- 扩展 API 功能

### 4. `C:\Users\21082\.claude\projects\...\memory\MEMORY.md`
**内容**：项目记忆文件（持久化上下文）
- **本地模式实现**：`--local_mode` 参数的添加位置
- **新项目结构**：lab-backend 和 node-red-contrib-unilab 的文件清单
- **环境变量**：UNILAB_URL, UNILAB_WS_URL, LAB_DB_PATH

**适用场景**：
- 快速回顾项目状态
- 查找已实现的功能
- 了解配置参数

---

## 核心架构

### 三层架构图

```
┌─────────────────────────────────────────────────────────────┐
│  应用层 (Application Layer)                                  │
│  - CLI: unilab --local_mode --backend ros -g devices.json   │
│  - Web: FastAPI (localhost:8002)                            │
│  - Node-RED: 可视化协议编辑器 (localhost:1880)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  编译层 (Compilation Layer)                                  │
│  - Workflow Compiler: convert_from_json.py                  │
│  - Device Registry: registry/*.yaml                         │
│  - Resource Manager: graphio.py, resource_tracker.py        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  执行层 (Execution Layer)                                    │
│  - Device Drivers: devices/*/                               │
│  - ROS2 Nodes: ros/nodes/                                   │
│  - Hardware Backends: PyLabRobot, Modbus, OPC-UA            │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户输入 (XDL/JSON/Node-RED Flow)
    ↓
[Workflow Compiler] + [Device Registry] + [Device Graph]
    ↓
设备操作序列 (transfer_liquid, heat_chill, ...)
    ↓
[Device Driver] + [PyLabRobot/Modbus/OPC-UA]
    ↓
硬件指令 (电机步数、泵阀开关、温度设定)
    ↓
物理设备执行
```

---

## 关键文件索引

### 配置与启动

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `unilabos/app/main.py` | CLI 入口 | 参数解析、启动流程、`--local_mode` 实现 (line 415-420) |
| `unilabos/config/config.py` | 配置类 | BasicConfig, WSConfig, HTTPConfig, `local_mode` 字段 (line 27) |
| `devices_graph.json` | 设备连接图 | 节点拓扑、父子关系、空间坐标、资源映射 |

### 工作流编译

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `unilabos/workflow/convert_from_json.py` | JSON → 设备操作 | ACTION_RESOURCE_MAPPING (line 35-54), 参数映射规则 |
| `unilabos/workflow/common.py` | 工作流图构建 | WorkflowGraph 类, build_protocol_graph() |
| `unilabos/workflow/wf_utils.py` | 工作流工具 | 拓扑排序、依赖解析 |

### 设备注册表

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `unilabos/registry/registry.py` | 注册表管理 | Registry 类, setup(), load_device_types() |
| `unilabos/registry/devices/*.yaml` | 设备定义 | 31 个设备类型，每个定义 action_value_mappings |
| `unilabos/registry/devices/liquid_handler.yaml` | 液体处理器 | 17 个操作定义（transfer_liquid, add_liquid, ...） |

### 设备驱动

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `unilabos/devices/liquid_handling/liquid_handler_abstract.py` | 液体处理抽象层 | transfer_liquid() (line 1100+), 三种传输模式 |
| `unilabos/devices/liquid_handling/prcxi/prcxi.py` | PRCXI 驱动 | PyLabRobot 后端实现 |
| `unilabos/devices/liquid_handling/prcxi/abstract_protocol.py` | 协议管理 | ProtocolManager, add_transfer(), compute_min_initials() |
| `unilabos/devices/virtual/*.py` | 虚拟设备 | 用于测试的模拟设备（heat_chill, pump, valve, ...） |

### 资源管理

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `unilabos/resources/graphio.py` | 设备图解析 | read_node_link_json(), canonicalize_nodes_data() |
| `unilabos/resources/resource_tracker.py` | 资源追踪 | ResourceTreeSet, ResourceDict |

### Web 服务

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `unilabos/app/web/api.py` | FastAPI 路由 | /api/v1/online-devices, /api/v1/job/add, /api/v1/job/{id}/status |
| `unilabos/app/web/server.py` | Web 服务器 | FastAPI app 初始化, CORS 配置 |
| `unilabos/app/web/client.py` | HTTP 客户端 | 与云端通信（local_mode 下跳过） |

### 新增项目

| 文件路径 | 功能 | 关键内容 |
|---------|------|---------|
| `lab-backend/main.py` | FastAPI 中间层 | 协议/任务管理 API, WebSocket 代理 |
| `lab-backend/lib/converter.py` | 格式转换 | Node-RED flow → UniLab job, 拓扑排序 |
| `node-red-contrib-unilab/nodes/*.js` | Node-RED 节点 | 9 个自定义节点（config, device-list, submit-job, ...） |

---

## 探索方法论

### 方法 1：从功能入手（推荐）

**场景**：我想知道 UniLab 如何实现液体转移

**步骤**：
1. **查询操作清单**：
   ```bash
   grep "transfer_liquid" UNILAB_SUPPORTED_OPERATIONS.md
   ```
   → 找到操作定义和参数

2. **查找注册表定义**：
   ```bash
   grep -A 20 "transfer_liquid:" unilabos/registry/devices/liquid_handler.yaml
   ```
   → 了解参数 schema 和默认值

3. **查找实现代码**：
   ```bash
   grep -rn "async def transfer_liquid" unilabos/devices/liquid_handling/
   ```
   → 找到 `liquid_handler_abstract.py:1100`

4. **阅读实现**：
   ```bash
   sed -n '1100,1300p' unilabos/devices/liquid_handling/liquid_handler_abstract.py
   ```
   → 理解编译逻辑

### 方法 2：从设备入手

**场景**：我想添加一个新的温控设备

**步骤**：
1. **查看现有设备**：
   ```bash
   ls unilabos/devices/temperature/
   ```
   → 找到 `chiller.py`, `sensor_node.py`

2. **查看注册表**：
   ```bash
   cat unilabos/registry/devices/temperature.yaml
   ```
   → 了解操作定义格式

3. **查看虚拟设备**：
   ```bash
   cat unilabos/devices/virtual/virtual_heatchill.py
   ```
   → 理解设备接口

4. **复制模板并修改**：
   ```bash
   cp unilabos/devices/virtual/virtual_heatchill.py unilabos/devices/temperature/my_heater.py
   # 修改类名、实现硬件通信
   ```

### 方法 3：从编译流程入手

**场景**：我想理解 workflow 如何转换为设备操作

**步骤**：
1. **阅读编译分析文档**：
   ```bash
   cat UNILAB_COMPILATION_ANALYSIS.md
   ```
   → 理解三层编译架构

2. **查看转换器代码**：
   ```bash
   cat unilabos/workflow/convert_from_json.py
   ```
   → 理解 ACTION_RESOURCE_MAPPING

3. **查看设备连接图**：
   ```bash
   cat devices_graph.json  # 如果存在
   ```
   → 理解节点拓扑和资源映射

4. **运行测试**：
   ```bash
   python -c "
   from unilabos.workflow.convert_from_json import convert_from_json
   result = convert_from_json('test_workflow.json')
   print(result.to_dict())
   "
   ```

### 方法 4：使用 Grep 快速定位

**常用搜索模式**：

```bash
# 查找所有异步函数
grep -rn "async def " unilabos/devices/ | head -50

# 查找特定操作的实现
grep -rn "def transfer_liquid" unilabos/

# 查找配置项
grep -rn "local_mode" unilabos/

# 查找设备类定义
find unilabos/devices -name "*.py" -exec grep -l "class.*Node\|class.*Device" {} \;

# 查找注册表中的操作
grep -E "^\s{6}[a-z_]+:" unilabos/registry/devices/liquid_handler.yaml | sed 's/://g'
```

---

## 常见任务指南

### 任务 1：启动 UniLab 本地模式

```bash
# 激活环境
mamba activate unilab

# 启动（跳过云端验证）
unilab --local_mode \
       --backend ros \
       --app_bridges fastapi \
       -g devices_graph.json \
       --upload_registry false

# 验证
curl http://localhost:8002/api/v1/online-devices
```

### 任务 2：提交一个液体转移任务

```bash
# 方法 A：直接调用 API
curl -X POST http://localhost:8002/api/v1/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "/PRCXI",
    "action": "transfer_liquid",
    "action_args": {
      "sources": [{"id": "/PRCXI/Deck/T4/A1"}],
      "targets": [{"id": "/PRCXI/Deck/T1/B1"}],
      "asp_vols": [100.0],
      "dis_vols": [100.0]
    }
  }'

# 方法 B：通过 lab-backend（需先启动）
cd lab-backend
uvicorn main:app --port 3000 &

curl -X POST http://localhost:3000/api/jobs/submit-single \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "/PRCXI",
    "action": "transfer_liquid",
    "action_args": {"asp_vol": 100, "dis_vol": 100, ...}
  }'
```

### 任务 3：查询任务状态

```bash
# 获取任务 ID（从上一步返回）
JOB_ID="abc-123-def-456"

# 查询状态
curl http://localhost:8002/api/v1/job/$JOB_ID/status

# 通过 lab-backend 查询（会自动同步 UniLab 状态）
curl http://localhost:3000/api/jobs/$JOB_ID/status
```

### 任务 4：创建一个 Node-RED 协议

```bash
# 1. 安装 Node-RED 节点
cd ~/.node-red
npm install /path/to/node-red-contrib-unilab

# 2. 启动 Node-RED
node-red

# 3. 在浏览器中打开 http://localhost:1880

# 4. 拖拽节点创建协议：
#    [unilab-transfer-liquid] → [unilab-incubation] → [unilab-submit-job]

# 5. 保存协议到 lab-backend
curl -X POST http://localhost:3000/api/protocols \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Prep Protocol",
    "description": "Transfer + Incubation",
    "flow_json": "[...]"  # Node-RED 导出的 JSON
  }'
```

### 任务 5：监控设备状态

```bash
# 方法 A：WebSocket 直连 UniLab
wscat -c ws://localhost:8002/api/v1/ws/device-status

# 方法 B：通过 lab-backend 代理
wscat -c ws://localhost:3000/ws/device-status

# 方法 C：在 Node-RED 中使用 unilab-device-monitor 节点
# （自动连接并推送到 Dashboard）
```

---

## 扩展开发指南

### 扩展 1：添加新的设备类型

**步骤**：

1. **创建设备驱动**：
   ```python
   # unilabos/devices/my_device/my_device.py
   from unilabos.ros.nodes.base_device_node import BaseROS2DeviceNode

   class MyDevice:
       _ros_node: BaseROS2DeviceNode

       def __init__(self, device_id: str, config: dict, **kwargs):
           self.device_id = device_id
           self.config = config

       def post_init(self, ros_node: BaseROS2DeviceNode):
           self._ros_node = ros_node

       async def initialize(self) -> bool:
           # 初始化硬件连接
           return True

       async def my_operation(self, param1: float, param2: str) -> dict:
           # 实现操作逻辑
           return {"success": True}
   ```

2. **创建注册表文件**：
   ```yaml
   # unilabos/registry/devices/my_device.yaml
   my_device:
     category:
       - custom
     class:
       action_value_mappings:
         my_operation:
           goal:
             param1: param1
             param2: param2
           goal_default:
             param1: 0.0
             param2: ""
           schema:
             properties:
               goal:
                 properties:
                   param1:
                     type: number
                   param2:
                     type: string
     module: "unilabos.devices.my_device.my_device:MyDevice"
     version: "1.0.0"
   ```

3. **添加到设备连接图**：
   ```json
   {
     "nodes": [
       {
         "id": "/MyDevice",
         "type": "device",
         "class": "my_device",
         "config": {"port": "COM3"}
       }
     ]
   }
   ```

4. **测试**：
   ```bash
   unilab --local_mode -g devices_graph.json
   curl -X POST http://localhost:8002/api/v1/job/add \
     -d '{"device_id": "/MyDevice", "action": "my_operation", "action_args": {"param1": 1.0, "param2": "test"}}'
   ```

### 扩展 2：添加新的 Node-RED 节点

**步骤**：

1. **创建节点定义**：
   ```javascript
   // node-red-contrib-unilab/nodes/unilab-my-operation.js
   module.exports = function(RED) {
       function MyOperationNode(config) {
           RED.nodes.createNode(this, config);
           const node = this;
           const backendCfg = RED.nodes.getNode(config.backend);

           node.on('input', async function(msg) {
               const payload = {
                   device_id: config.device_id,
                   action: "my_operation",
                   action_args: {
                       param1: config.param1,
                       param2: config.param2
                   }
               };

               try {
                   const res = await fetch(`${backendCfg.url}/api/jobs/submit-single`, {
                       method: 'POST',
                       headers: {'Content-Type': 'application/json'},
                       body: JSON.stringify(payload)
                   });
                   msg.payload = await res.json();
                   node.send(msg);
               } catch(err) {
                   node.error(err.message, msg);
               }
           });
       }
       RED.nodes.registerType("unilab-my-operation", MyOperationNode);
   };
   ```

2. **创建 HTML 界面**：
   ```html
   <!-- node-red-contrib-unilab/nodes/unilab-my-operation.html -->
   <script type="text/javascript">
       RED.nodes.registerType('unilab-my-operation', {
           category: 'UniLab操作',
           color: '#3498DB',
           defaults: {
               name: {value: ''},
               backend: {value: '', type: 'unilab-config'},
               device_id: {value: ''},
               param1: {value: 0.0},
               param2: {value: ''}
           },
           inputs: 1,
           outputs: 1,
           icon: 'font-awesome/fa-cog',
           label: function() { return this.name || '我的操作'; }
       });
   </script>

   <script type="text/html" data-template-name="unilab-my-operation">
       <div class="form-row">
           <label for="node-input-name"><i class="fa fa-tag"></i> 名称</label>
           <input type="text" id="node-input-name">
       </div>
       <div class="form-row">
           <label for="node-input-backend"><i class="fa fa-server"></i> 后端</label>
           <input type="text" id="node-input-backend">
       </div>
       <div class="form-row">
           <label for="node-input-device_id"><i class="fa fa-microchip"></i> 设备 ID</label>
           <input type="text" id="node-input-device_id">
       </div>
       <div class="form-row">
           <label for="node-input-param1"><i class="fa fa-sliders"></i> 参数1</label>
           <input type="number" id="node-input-param1">
       </div>
       <div class="form-row">
           <label for="node-input-param2"><i class="fa fa-font"></i> 参数2</label>
           <input type="text" id="node-input-param2">
       </div>
   </script>
   ```

3. **注册到 package.json**：
   ```json
   {
     "node-red": {
       "nodes": {
         "unilab-my-operation": "nodes/unilab-my-operation.js"
       }
     }
   }
   ```

### 扩展 3：添加新的 lab-backend API

**步骤**：

1. **创建路由**：
   ```python
   # lab-backend/routers/my_feature.py
   from fastapi import APIRouter, Depends
   from database import get_db

   router = APIRouter()

   @router.get("/my-endpoint")
   async def my_endpoint(db=Depends(get_db)):
       # 实现逻辑
       return {"result": "success"}
   ```

2. **挂载路由**：
   ```python
   # lab-backend/main.py
   from routers import my_feature

   app.include_router(my_feature.router, prefix="/api/my-feature", tags=["MyFeature"])
   ```

3. **测试**：
   ```bash
   curl http://localhost:3000/api/my-feature/my-endpoint
   ```

---

## 调试技巧

### 技巧 1：启用详细日志

```python
# 修改 unilabos/config/config.py
class BasicConfig:
    log_level = "TRACE"  # 或 "DEBUG"
```

### 技巧 2：使用虚拟设备测试

```bash
# 使用虚拟液体处理器（不需要真实硬件）
unilab --local_mode --backend simple -g virtual_devices.json
```

### 技巧 3：查看 ROS2 节点状态

```bash
# 列出所有节点
ros2 node list

# 查看节点信息
ros2 node info /PRCXI

# 查看话题
ros2 topic list
ros2 topic echo /device_status
```

### 技巧 4：使用 Python 交互式调试

```python
# 启动 Python REPL
python

# 导入并测试编译器
from unilabos.workflow.convert_from_json import convert_from_json
graph = convert_from_json('test_workflow.json')
print(graph.to_dict())

# 测试设备驱动
from unilabos.devices.virtual.virtual_heatchill import VirtualHeatChill
device = VirtualHeatChill(device_id="test")
import asyncio
asyncio.run(device.initialize())
asyncio.run(device.heat_chill(temp=80, time=3600, stir=True, stir_speed=300, purpose="test"))
```

---

## 常见问题

### Q1: 如何跳过云端验证？
**A**: 使用 `--local_mode` 参数启动 UniLab（已在 `main.py:415-420` 实现）

### Q2: 设备连接图在哪里？
**A**: 通过 `-g` 参数指定，通常是 `devices_graph.json`。格式参考 `unilabos/resources/graphio.py`

### Q3: 如何查看支持的操作？
**A**: 查看 `UNILAB_SUPPORTED_OPERATIONS.md` 或对应设备的 YAML 文件

### Q4: 如何添加新操作？
**A**:
1. 在设备驱动中实现 `async def my_operation(...)`
2. 在 `registry/devices/*.yaml` 中添加操作定义
3. 在 `workflow/convert_from_json.py` 的 `ACTION_RESOURCE_MAPPING` 中添加映射（如果需要）

### Q5: 如何调试编译错误？
**A**:
1. 检查 `workflow/convert_from_json.py` 的参数映射
2. 检查 `registry/devices/*.yaml` 的 schema 定义
3. 启用 TRACE 日志查看详细编译过程

---

## 下一步行动

### 对于理解系统的 Agent
1. 阅读 `UNILAB_COMPILATION_ANALYSIS.md` 理解编译机制
2. 阅读 `UNILAB_SUPPORTED_OPERATIONS.md` 了解支持的操作
3. 使用本文档的"探索方法论"深入研究感兴趣的模块

### 对于扩展功能的 Agent
1. 参考"扩展开发指南"添加新设备/操作/节点
2. 使用"调试技巧"验证实现
3. 更新相关文档（YAML、README）

### 对于集成系统的 Agent
1. 启动 UniLab 本地模式
2. 启动 lab-backend
3. 安装 Node-RED 节点
4. 参考"常见任务指南"完成端到端测试

---

## 联系与反馈

- **项目路径**：`C:\Users\21082\PycharmProjects\Uni-Lab-OS`
- **文档位置**：项目根目录下的 `*.md` 文件
- **记忆文件**：`C:\Users\21082\.claude\projects\...\memory\MEMORY.md`

**建议**：在开始任何开发前，先运行一次完整的测试流程，确保环境配置正确。
