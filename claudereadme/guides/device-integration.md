# UniLab 设备集成指南

> **目标**：将新设备集成到 UniLab 系统
> **难度**：⭐⭐⭐ 高级

---

## 概述

集成新设备到 UniLab 需要完成以下步骤：

1. 开发设备驱动（Python 类）
2. 创建设备注册表（YAML 配置）
3. 更新设备连接图
4. 测试设备功能
5. 编写操作文档

---

## 步骤 1：开发设备驱动

### 选择设备类别

根据设备类型选择合适的目录：

```
unilabos/devices/
├── liquid_handling/     # 液体处理器
├── temperature/         # 温控设备
├── pump_and_valve/      # 泵和阀
├── arm/                 # 机械臂
├── hplc/                # 色谱仪
├── balance/             # 天平
└── virtual/             # 虚拟/测试设备
```

### 基本驱动模板

**文件位置**：`unilabos/devices/[category]/[device_name].py`

```python
import asyncio
from typing import Dict, Any, Optional
from unilabos.ros.nodes.base_device_node import BaseROS2DeviceNode


class MyDevice:
    """My custom device driver"""

    _ros_node: BaseROS2DeviceNode

    def __init__(self, device_id: str = None, config: Dict[str, Any] = None, **kwargs):
        self.device_id = device_id or "unknown_device"
        self.config = config or {}
        self.data = {}
        # 从 config 读取设备参数
        self.port = self.config.get('port', 'COM1')
        self.baudrate = self.config.get('baudrate', 9600)
        print(f"[{self.device_id}] 设备已创建")

    def post_init(self, ros_node: BaseROS2DeviceNode):
        """ROS2 节点初始化后调用"""
        self._ros_node = ros_node

    async def initialize(self) -> bool:
        """初始化设备硬件连接"""
        try:
            # TODO: 连接设备、初始化通信
            self.data['status'] = 'initialized'
            return True
        except Exception as e:
            self.data['status'] = 'error'
            return False

    async def cleanup(self) -> bool:
        """清理资源，断开连接"""
        self.data['status'] = 'offline'
        return True

    async def my_operation(self, param1: float, param2: str) -> bool:
        """自定义操作示例"""
        # 1. 验证参数
        if param1 < 0:
            raise ValueError(f"param1 must be positive, got {param1}")
        # 2. 发送命令
        self.data['last_operation'] = {'param1': param1, 'param2': param2}
        # TODO: 实现实际硬件操作
        await asyncio.sleep(0.1)  # 模拟操作延迟
        return True
```

### 必需方法说明

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `__init__` | 构造函数，读取配置参数 | - |
| `post_init(ros_node)` | ROS2 节点注入 | - |
| `initialize()` | 连接设备、初始化状态 | bool |
| `cleanup()` | 释放资源、断开连接 | bool |
| `my_operation(...)` | 业务操作（按需实现） | 任意 |

---

## 步骤 2：创建设备注册表

**文件位置**：`unilabos/registry/devices/[device_name].yaml`

### 最小模板

```yaml
my_device:
  category:
    - my_category
  class:
    action_value_mappings:
      my_operation:
        feedback: {}
        goal:
          param1: param1
          param2: param2
        goal_default:
          param1: 0.0
          param2: ""
        handles: {}
        result:
          success: success
        schema:
          description: "My custom operation"
          properties:
            goal:
              properties:
                param1:
                  type: number
                param2:
                  type: string
              required:
                - param1
              type: object
            result:
              properties:
                success:
                  type: boolean
              type: object
          type: object
        type: UniLabJsonCommandAsync
  config_info: []
  description: "My custom device"
  handles: []
  icon: icon_device.webp
  init_param_schema:
    properties:
      port:
        default: COM1
        type: string
      baudrate:
        default: 9600
        type: integer
    type: object
  module: "unilabos.devices.my_category.my_device:MyDevice"
  version: 1.0.0
```

### 关键字段说明

| 字段 | 必须 | 说明 |
|------|------|------|
| `module` | ✅ | Python 导入路径，格式 `package.module:ClassName` |
| `action_value_mappings` | ✅ | 所有操作的定义 |
| `goal` | ✅ | 操作参数映射（`yaml_key: python_param`） |
| `goal_default` | ✅ | 参数默认值 |
| `schema.goal.properties` | ✅ | 参数 JSON Schema |
| `type` | ✅ | `UniLabJsonCommandAsync`（异步）或 `UniLabJsonCommand` |
| `init_param_schema` | ❌ | 设备初始化参数（设备图 config 字段的验证） |

---

## 步骤 3：更新设备连接图

在 `devices_graph.json` 中添加设备节点：

```json
{
  "nodes": [
    {
      "id": "/MyDevice",
      "type": "device",
      "name": "MyDevice",
      "class": "my_device",
      "config": {
        "port": "COM3",
        "baudrate": 115200
      }
    }
  ],
  "links": []
}
```

如果设备有子资源（如槽位、通道）：

```json
{
  "nodes": [
    {"id": "/MyDevice", "type": "device", "class": "my_device"},
    {
      "id": "/MyDevice/Channel1",
      "type": "resource_holder",
      "parent": "/MyDevice",
      "position": {"x": 0, "y": 0, "z": 0}
    }
  ]
}
```

---

## 步骤 4：测试设备

### 单元测试

**文件位置**：`unilabos/devices/[category]/test_[device_name].py`

```python
import asyncio
import pytest
from unilabos.devices.my_category.my_device import MyDevice


@pytest.mark.asyncio
async def test_initialize():
    device = MyDevice(device_id="test", config={"port": "COM1"})
    result = await device.initialize()
    assert result is True


@pytest.mark.asyncio
async def test_my_operation():
    device = MyDevice(device_id="test")
    await device.initialize()
    result = await device.my_operation(param1=10.0, param2="hello")
    assert result is True
    await device.cleanup()
```

运行测试：

```bash
pytest unilabos/devices/my_category/test_my_device.py -v
```

### 集成测试

```bash
# 启动 UniLab
unilab --local_mode -g devices_graph.json --backend ros --app_bridges fastapi

# 验证设备在线
curl http://localhost:8002/api/v1/online-devices

# 提交任务
curl -X POST http://localhost:8002/api/v1/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "/MyDevice",
    "action": "my_operation",
    "action_args": {"param1": 10.0, "param2": "test"}
  }'
```

---

## 完整示例：虚拟温控设备

UniLab 内置了多个虚拟设备作为参考，以 `VirtualHeatChill` 为例：

### 驱动文件

`unilabos/devices/virtual/virtual_heatchill.py`

- 实现了 `initialize`, `cleanup`, `heat_chill` 方法
- `heat_chill` 参数：`temp`, `time`, `stir`, `stir_speed`
- 模拟加热过程（不连接真实硬件）

### 注册表文件

`unilabos/registry/devices/virtual_device.yaml`

- `module: "unilabos.devices.virtual.virtual_heatchill:VirtualHeatChill"`
- 定义了 `heat_chill` 操作的参数 schema

### 参考路径

```
查看驱动实现：
unilabos/devices/virtual/virtual_heatchill.py

查看注册表定义：
unilabos/registry/devices/virtual_device.yaml

查看液体处理器（复杂案例）：
unilabos/devices/liquid_handling/liquid_handler_abstract.py
unilabos/registry/devices/liquid_handler.yaml
```

---

## 最佳实践

### 错误处理

```python
async def my_operation(self, param1: float) -> bool:
    logger = self._ros_node.lab_logger() if hasattr(self, '_ros_node') else None
    try:
        if param1 < 0:
            raise ValueError(f"param1 must be >= 0, got {param1}")
        # 执行操作
        await asyncio.sleep(0.1)
        if logger:
            logger.info(f"[{self.device_id}] 操作完成: param1={param1}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"[{self.device_id}] 操作失败: {e}")
        self.data['last_error'] = str(e)
        return False
```

### 状态管理

```python
def __init__(self, ...):
    self.data = {
        'status': 'offline',         # offline / initialized / busy / error
        'last_operation': None,
        'last_error': None,
    }

async def my_operation(self, ...):
    self.data['status'] = 'busy'
    try:
        await self._do_work()
        self.data['status'] = 'initialized'
        return True
    except Exception as e:
        self.data['status'] = 'error'
        self.data['last_error'] = str(e)
        return False
```

### 参数验证

在方法开头验证所有参数，早发现早报错：

```python
async def heat_chill(self, temp: float, time: float, stir_speed: float) -> bool:
    assert self._min_temp <= temp <= self._max_temp, \
        f"temp {temp} out of range [{self._min_temp}, {self._max_temp}]"
    assert time >= 0, f"time must be non-negative, got {time}"
    assert 0 <= stir_speed <= self._max_stir_speed, \
        f"stir_speed {stir_speed} out of range [0, {self._max_stir_speed}]"
    # ... 执行操作
```

---

## 故障排查

### 设备未出现在在线列表

1. 检查 YAML 的 `module` 路径是否可导入：
   ```bash
   python -c "from unilabos.devices.my_category.my_device import MyDevice; print('OK')"
   ```
2. 检查 `devices_graph.json` 中的 `class` 是否与 YAML key 对应
3. 查看 UniLab 启动日志，搜索设备 ID

### 操作无法调用

1. 确认 YAML 中定义了该操作名
2. 确认 Python 方法签名与 YAML `goal` 中的参数一致
3. 确认方法是 `async def`

### 参数验证失败

1. 检查 schema 中 `required` 列表
2. 检查参数类型（`number`/`integer`/`string`/`boolean`/`array`/`object`）
3. 检查 `goal_default` 是否与类型匹配

---

## 参考资源

| 资源 | 路径 |
|------|------|
| 虚拟设备示例 | `unilabos/devices/virtual/` |
| 液体处理器（复杂参考） | `unilabos/devices/liquid_handling/liquid_handler_abstract.py` |
| 注册表示例（完整） | `unilabos/registry/devices/liquid_handler.yaml` |
| 探索指南 | `claudereadme/EXPLORATION_GUIDE.md` |
| 操作清单 | `claudereadme/architecture/UNILAB_SUPPORTED_OPERATIONS.md` |
