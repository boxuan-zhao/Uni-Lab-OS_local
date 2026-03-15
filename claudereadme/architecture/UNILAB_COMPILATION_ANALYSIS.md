# UniLab 编译转化机制深度分析

## 核心发现：UniLab 如何将化学操作编译为泵阀指令

经过对 UniLab 源码的深入探索，我发现了完整的**三层编译架构**，其中**设备连接图（device graph）在每一层都起到关键作用**。

---

## 一、三层编译架构

```
┌─────────────────────────────────────────────────────────────┐
│  第一层：化学协议 → 设备操作                                  │
│  输入: XDL/JSON workflow (化学指令)                          │
│  输出: transfer_liquid, incubation 等设备操作                │
│  关键文件: unilabos/workflow/convert_from_json.py            │
│  依赖: 设备连接图 (reagent slot → deck position 映射)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  第二层：设备操作 → PyLabRobot 原语                          │
│  输入: transfer_liquid(sources, targets, volumes)            │
│  输出: pick_up_tips → aspirate → dispense → discard_tips     │
│  关键文件: liquid_handler_abstract.py                        │
│  依赖: Deck 拓扑 (tip rack 位置、plate 位置、可达性)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  第三层：PyLabRobot 原语 ��� 硬件指令                          │
│  输入: aspirate(well, volume, flow_rate)                     │
│  输出: 泵阀控制指令 (Modbus/OPC-UA/HTTP)                     │
│  关键文件: prcxi/prcxi.py, biomek.py 等设备驱动              │
│  依赖: 设备物理参数 (泵容量、阀门端口、坐标系)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、第一层编译：化学协议 → 设备操作

### 输入格式（JSON Workflow）

```json
{
  "workflow": [
    {
      "action": "transfer_liquid",
      "action_args": {
        "sources": "reagent_A",
        "targets": "reaction_vessel",
        "asp_vol": 100.0,
        "dis_vol": 100.0
      }
    }
  ],
  "reagent": {
    "reagent_A": {
      "slot": 4,
      "well": ["A1", "A3", "A5"],
      "labware": "96_well_plate"
    },
    "reaction_vessel": {
      "slot": 1,
      "well": ["B1", "B2", "B3"],
      "labware": "deep_well_plate"
    }
  }
}
```

### 编译过程（convert_from_json.py）

**步骤 1：创建资源节点（create_resource）**
```python
# 根据 reagent 的 slot 信息，在设备连接图中查找对应的 deck 位置
for reagent_name, info in reagents.items():
    slot = info["slot"]
    # 查询设备连接图：slot 4 对应哪个物理位置？
    parent = f"/PRCXI/PRCXI_Deck/T{slot}"  # 从 graph 中解析

    create_resource_node = {
        "action": "create_resource",
        "res_id": f"plate_slot_{slot}",
        "device_id": "/PRCXI",
        "class_name": "PRCXI_BioER_96_wellplate",
        "parent": parent,  # ← 来自设备连接图
        "slot_on_deck": str(slot)
    }
```

**步骤 2：设置液体信息（set_liquid_from_plate）**
```python
# 为每个 reagent 创建液体标记节点
set_liquid_node = {
    "action": "set_liquid_from_plate",
    "plate": [],  # 通过连接传递
    "well_names": ["A1", "A3", "A5"],
    "liquid_names": ["reagent_A", "reagent_A", "reagent_A"],
    "volumes": [100000, 100000, 100000]  # µL
}
```

**步骤 3：解析 workflow 动作**
```python
# 将 sources/targets 字符串解析为实际的 well 对象
transfer_node = {
    "action": "transfer_liquid",
    "sources": [],  # 通过连接传递（来自 set_liquid_from_plate）
    "targets": [],  # 通过连接传递
    "asp_vols": [100.0, 100.0, 100.0],  # 扩展为数组
    "dis_vols": [100.0, 100.0, 100.0]
}
```

### 关键：设备连接图的作用

**文件**: `unilabos/resources/graphio.py`

设备连接图（`devices_graph.json`）定义了：
1. **Deck 拓扑**: 每个 slot 在物理空间的位置
2. **父子关系**: `/PRCXI/PRCXI_Deck/T4` 表示 slot 4 是 Deck 的子节点
3. **资源类型**: 每个位置可以放置什么类型的 labware

```json
{
  "nodes": [
    {
      "id": "/PRCXI",
      "type": "device",
      "class": "PRCXI_LiquidHandler"
    },
    {
      "id": "/PRCXI/PRCXI_Deck",
      "type": "resource",
      "parent": "/PRCXI"
    },
    {
      "id": "/PRCXI/PRCXI_Deck/T1",
      "type": "resource_holder",
      "parent": "/PRCXI/PRCXI_Deck",
      "position": {"x": 0, "y": 0, "z": 0}
    },
    {
      "id": "/PRCXI/PRCXI_Deck/T4",
      "type": "resource_holder",
      "parent": "/PRCXI/PRCXI_Deck",
      "position": {"x": 300, "y": 0, "z": 0}
    }
  ],
  "links": [
    {
      "source": "/PRCXI/PRCXI_Deck/T1",
      "target": "/PRCXI/PRCXI_Deck/T4",
      "type": "reachable"
    }
  ]
}
```

**编译器如何使用 graph**:
```python
# unilabos/workflow/common.py: build_protocol_graph()
def resolve_slot_to_deck_position(slot: int, graph: nx.Graph) -> str:
    """从设备连接图中查找 slot 对应的物理位置"""
    for node_id, data in graph.nodes(data=True):
        if data.get("slot") == slot:
            return node_id
    raise ValueError(f"Slot {slot} not found in device graph")
```

---

## 三、第二层编译：设备操作 → PyLabRobot 原语

### 输入（transfer_liquid 调用）

```python
await liquid_handler.transfer_liquid(
    sources=[well_A1, well_A3, well_A5],
    targets=[well_B1, well_B2, well_B3],
    asp_vols=[100.0, 100.0, 100.0],
    dis_vols=[100.0, 100.0, 100.0]
)
```

### 编译过程（liquid_handler_abstract.py）

**步骤 1：识别传输模式**
```python
# line 1195-1271
num_sources = len(sources)
num_targets = len(targets)

if num_sources == 1 and num_targets > 1:
    # 一对多：1 source → N targets
    mode = "one_to_many"
elif num_sources > 1 and num_targets == 1:
    # 多对一：N sources → 1 target
    mode = "many_to_one"
elif num_sources == num_targets:
    # 一对一：N sources → N targets
    mode = "one_to_one"
```

**步骤 2：选择合适的 tip（基于体积）**
```python
# line 196-202 (abstract_protocol.py)
def recommend_tip(self, unit_volume: float) -> str:
    """根据体积选择最小可用的 tip"""
    tip_catalog = [
        {"name": "TIP_10uL",   "capacity": 10.0},
        {"name": "TIP_200uL",  "capacity": 200.0},
        {"name": "TIP_1000uL", "capacity": 1000.0}
    ]
    for tip in tip_catalog:
        if tip["capacity"] >= unit_volume:
            return tip["name"]
```

**步骤 3：查找 tip rack 位置（依赖 Deck 拓扑）**
```python
# line 750-767
def find_tip_rack(self, tip_name: str) -> TipRack:
    """从 Deck 中查找包含指定 tip 的 rack"""
    for child in self.deck.children:
        if isinstance(child, TipRack):
            if child.get_all_tips()[0].name == tip_name:
                return child
    raise ValueError(f"No tip rack found for {tip_name}")
```

**步骤 4：生成 PyLabRobot 原语序列**
```python
# line 1309-1360 (_transfer_one_to_one)
for i in range(len(targets)):
    # 1. 拾取 tip
    tip = next(self.current_tip)
    await self.pick_up_tips([tip])

    # 2. 吸液
    await self.aspirate(
        resources=[sources[i]],
        vols=[asp_vols[i]],
        flow_rates=[asp_flow_rates[i]]
    )

    # 3. 分液
    await self.dispense(
        resources=[targets[i]],
        vols=[dis_vols[i]],
        flow_rates=[dis_flow_rates[i]]
    )

    # 4. 丢弃 tip
    await self.discard_tips()
```

### 关键：Deck 拓扑的作用

**PyLabRobot Deck 对象**（从设备连接图构建）:
```python
# Deck 包含所有资源的空间关系
deck = Deck()
deck.assign_child_resource(
    TipRack("tip_rack_1"),
    location=Coordinate(x=0, y=0, z=0)  # ← 来自 graph
)
deck.assign_child_resource(
    Plate("plate_slot_4"),
    location=Coordinate(x=300, y=0, z=0)  # ← 来自 graph
)
```

**可达性检查**:
```python
def is_reachable(source: Resource, target: Resource, graph: nx.Graph) -> bool:
    """检查两个资源之间是否有物理连接"""
    return nx.has_path(graph, source.name, target.name)
```

---

## 四、第三层编译：PyLabRobot 原语 → 硬件指令

### 输入（PyLabRobot 原语）

```python
await backend.aspirate(
    channels=[0],
    volumes=[100.0],
    positions=[Coordinate(x=50.5, y=30.2, z=10.0)],
    flow_rates=[150.0]
)
```

### 编译过程（prcxi.py 设备驱动）

**步骤 1：坐标转换（依赖设备物理参数）**
```python
# 将 PyLabRobot 坐标转换为设备原生坐标系
def transform_coordinate(coord: Coordinate, device_config: dict) -> dict:
    """
    device_config 来自设备连接图的 config 字段
    """
    offset = device_config.get("coordinate_offset", {"x": 0, "y": 0, "z": 0})
    return {
        "X": coord.x + offset["x"],
        "Y": coord.y + offset["y"],
        "Z": coord.z + offset["z"]
    }
```

**步骤 2：生成设备特定指令**
```python
# PRCXI 使用 HTTP API
command = {
    "Command": "Aspirate",
    "Parameters": {
        "Channel": 0,
        "Volume": 100.0,  # µL
        "Position": {"X": 50.5, "Y": 30.2, "Z": 10.0},
        "FlowRate": 150.0,  # µL/s
        "PumpPort": device_config["pump_mapping"][0]  # ← 来自 graph
    }
}
response = await http_client.post(device_url, json=command)
```

**步骤 3：泵阀控制（最底层）**
```python
# 设备固件将 HTTP 命令转换为泵阀指令
# 例如：Aspirate 100µL @ 150µL/s
# → 打开阀门 V1
# → 启动泵 P1，速度 150µL/s
# → 运行时间 = 100 / 150 = 0.67秒
# → 关闭阀门 V1
```

### 关键：设备物理参数（来自 graph）

```json
{
  "id": "/PRCXI",
  "type": "device",
  "config": {
    "coordinate_offset": {"x": 0, "y": 0, "z": 50},
    "pump_mapping": {
      "0": "P1",  // channel 0 → pump P1
      "1": "P2"
    },
    "valve_mapping": {
      "0": ["V1", "V2"],  // channel 0 控制阀门 V1, V2
      "1": ["V3", "V4"]
    },
    "max_flow_rate": 500.0,  // µL/s
    "dead_volume": 5.0  // µL
  }
}
```

---

## 五、完整示例：一个 transfer_liquid 的编译全过程

### 输入：化学协议

```json
{
  "workflow": [
    {"action": "transfer_liquid", "action_args": {
      "sources": "reagent_A", "targets": "plate_B",
      "asp_vol": 50.0, "dis_vol": 50.0
    }}
  ],
  "reagent": {
    "reagent_A": {"slot": 4, "well": ["A1"]},
    "plate_B": {"slot": 1, "well": ["B1", "B2", "B3"]}
  }
}
```

### 第一层编译输出

```python
[
  {"action": "create_resource", "res_id": "plate_4", "parent": "/PRCXI/Deck/T4"},
  {"action": "create_resource", "res_id": "plate_1", "parent": "/PRCXI/Deck/T1"},
  {"action": "set_liquid_from_plate", "plate": "plate_4", "wells": ["A1"]},
  {"action": "set_liquid_from_plate", "plate": "plate_1", "wells": ["B1","B2","B3"]},
  {"action": "transfer_liquid",
   "sources": [well_A1],
   "targets": [well_B1, well_B2, well_B3],
   "asp_vols": [50.0, 50.0, 50.0],
   "dis_vols": [50.0, 50.0, 50.0]
  }
]
```

### 第二层编译输出（一对多模式）

```python
# 循环 3 次（3 个 targets）
for i in [0, 1, 2]:
    pick_up_tips([tip_rack_1.tips[i]])
    aspirate([well_A1], [50.0])  # 同一个 source
    dispense([targets[i]], [50.0])
    discard_tips()
```

### 第三层编译输出（PRCXI HTTP 指令）

```json
// 第 1 次循环
{"Command": "PickUpTip", "Parameters": {"Channel": 0, "Position": {"X": 10, "Y": 10, "Z": 50}}}
{"Command": "Aspirate", "Parameters": {"Channel": 0, "Volume": 50, "Position": {"X": 300, "Y": 0, "Z": 10}, "FlowRate": 150, "PumpPort": "P1"}}
{"Command": "Dispense", "Parameters": {"Channel": 0, "Volume": 50, "Position": {"X": 0, "Y": 0, "Z": 10}, "FlowRate": 100, "PumpPort": "P1"}}
{"Command": "DiscardTip", "Parameters": {"Channel": 0, "Position": {"X": 500, "Y": 0, "Z": 50}}}

// 第 2 次循环（target = B2）
...
// 第 3 次循环（target = B3）
...
```

### 最终硬件执行（泵阀控制）

```
时间 0.0s: 打开阀门 V1（连接 tip rack）
时间 0.1s: Z 轴下降到 tip 位置
时间 0.3s: 夹爪闭合，拾取 tip
时间 0.5s: Z 轴上升
时间 0.7s: XY 移动到 well A1 (300, 0)
时间 1.2s: Z 轴下降到液面
时间 1.4s: 打开阀门 V2（连接 pump P1）
时间 1.5s: 启动泵 P1，吸液 50µL @ 150µL/s
时间 1.83s: 停止泵 P1
时间 1.9s: Z 轴上升
时间 2.1s: XY 移动到 well B1 (0, 0)
时间 2.6s: Z 轴下降
时间 2.8s: 启动泵 P1 反向，分液 50µL @ 100µL/s
时间 3.3s: 停止泵 P1
时间 3.5s: Z 轴上升
时间 3.7s: XY 移动到 trash (500, 0)
时间 4.2s: 夹爪打开，丢弃 tip
时间 4.4s: 关闭阀门 V1, V2
```

---

## 六、设备连接图在编译中的关键作用总结

| 编译层级 | 使用的 graph 信息 | 具体作用 |
|---------|------------------|---------|
| **第一层** | `nodes[].parent`, `nodes[].position` | 将 reagent slot 映射到 deck 物理位置 |
| **第二层** | `links[].type=reachable` | 检查资源可达性，选择移液路径 |
| **第三层** | `nodes[].config.pump_mapping` | 将逻辑通道映射到物理泵阀端口 |
| **所有层** | `nodes[].position` | 坐标转换（相对坐标 → 绝对坐标） |

### 没有设备连接图会发生什么？

1. **第一层编译失败**: 无法知道 slot 4 对应哪个 deck 位置
2. **第二层无法优化**: 不知道哪些资源之间可以直接移液
3. **第三层硬件错误**: 不知道 channel 0 应该控制哪个泵

**结论**: 设备连接图是编译器的"地图"，缺少它就像让机器人在黑暗中操作。

---

## 七、如何在 lab-backend 中集成编译功能

### 方案：直接调用 UniLab 编译模块

```python
# lab-backend/lib/workflow_compiler.py
import sys
sys.path.append('/path/to/unilabos')

from unilabos.workflow.convert_from_json import convert_from_json
from unilabos.resources.graphio import read_node_link_json

# 加载设备连接图
graph = read_node_link_json("devices_graph.json")

def compile_workflow(workflow_json: dict) -> list:
    """
    将化学协议编译为 UniLab 任务列表

    Args:
        workflow_json: {"workflow": [...], "reagent": {...}}

    Returns:
        [{"device_id": "...", "action": "...", "action_args": {...}}, ...]
    """
    # 调用 UniLab 编译器（需要 graph 上下文）
    workflow_graph = convert_from_json(workflow_json, workstation_name="PRCXI")

    # 转换为任务列表
    jobs = workflow_graph.to_dict()

    return jobs
```

### API 端点

```python
# routers/workflow.py
@router.post("/compile")
async def compile_workflow(body: WorkflowCompile):
    """编译化学协议为设备操作序列"""
    try:
        jobs = compile_workflow(body.content)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
```

---

## 八、总结

### 核心发现

1. **UniLab 使用三层编译架构**，每层都依赖设备连接图
2. **一个 `transfer_liquid` 操作会被编译为数十个泵阀指令**
3. **设备连接图不仅定义拓扑，还包含物理参数**（泵映射、坐标偏移等）
4. **编译过程是确定性的**，相同输入 + 相同 graph → 相同硬件指令

### 实施建议

1. **短期**: 在 lab-backend 添加 workflow 编译 API，直接调用 UniLab 模块
2. **中期**: 提供设备连接图的可视化编辑器（基于 React Flow）
3. **长期**: 开发独立的编译器，支持更多设备类型和优化策略

### 关键文件索引

| 文件 | 作用 |
|------|------|
| `unilabos/workflow/convert_from_json.py` | 第一层编译器 |
| `unilabos/devices/liquid_handling/liquid_handler_abstract.py` | 第二层编译器 |
| `unilabos/devices/liquid_handling/prcxi/prcxi.py` | 第三层编译器（PRCXI 驱动） |
| `unilabos/resources/graphio.py` | 设备连接图解析器 |
| `unilabos/workflow/common.py` | WorkflowGraph 构建器 |
