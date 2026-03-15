# Node-RED 自定义节点说明

> **包名称**：node-red-contrib-unilab
> **版本**：0.1.0
> **节点数量**：9 个

---

## 概述

`node-red-contrib-unilab` 是为 UniLab 实验室自动化系统开发的 Node-RED 自定义节点包，提供可视化的实验协议编辑和设备控制功能。

### 系统架构

```
Node-RED (localhost:1880)
    ↕ HTTP REST + WebSocket
lab-backend (localhost:3000)
    ↕ HTTP REST + WebSocket
UniLab (localhost:8002)
    ↕ 设备协议
实验室设备
```

---

## 节点分类

### 1. 配置节点

#### `unilab-config`
**类型**：配置节点（不显示在画布上）

**功能**：存储 lab-backend 的连接信息

**配置参数**：
- `name`：配置名称（如 "UniLab Backend"）
- `url`：后端 URL（默认 `http://localhost:3000`）

**使用方式**：
其他所有节点通过此配置节点连接到 lab-backend。

---

### 2. 控制节点

#### `unilab-submit-job`
**类别**：UniLab
**颜色**：绿色 (#27AE60)
**图标**：fa-play

**功能**：提交协议到 UniLab 执行

**输入**：
- `msg.protocolId`：协议 ID（可选，优先级高于节点配置）

**输出**：
- `msg.payload`：提交结果
  ```json
  {
    "protocol_id": "xxx",
    "jobs": [
      {"id": "job1", "unilab_job_id": "...", "device_id": "...", "action": "..."},
      {"id": "job2", ...}
    ]
  }
  ```
- `msg.jobIds`：任务 ID 数组 `["job1", "job2", ...]`

**配置参数**：
- `backend`：后端配置节点
- `protocolId`：协议 ID（可被 `msg.protocolId` 覆盖）

**状态显示**：
- 蓝色圆点：提交中
- 绿色圆点：已提交 N 个任务
- 红色圆圈：提交失败

**示例流程**：
```
[inject] → [unilab-submit-job] → [debug]
```

---

#### `unilab-job-status`
**类别**：UniLab
**颜色**：橙色 (#F39C12)
**图标**：fa-tasks

**功能**：轮询任务状态直到完成

**输入**：
- `msg.jobId`���单个任务 ID
- `msg.jobIds`：任务 ID 数组（批量查询）

**输出**：
- **输出 1（成功）**：任务状态为 4（success）
  ```json
  {
    "payload": {
      "id": "job1",
      "status": 4,
      "unilab_data": {...}
    },
    "jobStatus": 4
  }
  ```
- **输出 2（失败）**：任务状态为 5（cancelled）或 6（aborted）

**配置参数**：
- `backend`：后端配置节点
- `jobId`：任务 ID（可被 `msg.jobId` 覆盖）
- `pollInterval`：轮询间隔（秒，默认 5）

**状态显示**：
- 蓝色圆点：轮询中
- 黄色圆点：执行中
- 绿色圆点：成功
- 红色圆点：失败

**示例流程**：
```
[unilab-submit-job] → [unilab-job-status] → [成功] → [dashboard通知]
                                           → [失败] → [错误处理]
```

---

### 3. 监控节点

#### `unilab-device-monitor`
**类别**：UniLab
**颜色**：紫色 (#8E44AD)
**图标**：fa-heartbeat

**功能**：通过 WebSocket 实时接收设备状态

**输入**：无（0 个输入）

**输出**：
- `msg.payload`：设备状态 JSON
  ```json
  {
    "devices": [
      {"id": "/PRCXI", "status": "online", "temperature": 25.3},
      {"id": "/Heater", "status": "running", "setpoint": 80}
    ],
    "timestamp": "2026-03-15T10:30:00Z"
  }
  ```
- `msg.topic`：固定为 `"device-status"`

**配置参数**：
- `backend`：后端配置节点

**状态显示**：
- 黄色圆圈：连接中
- 绿色圆点：已连接
- 红色圆圈：已断开，重连中

**特性**：
- 自动重连（断线后 5 秒重试）
- 新连接时立即推送最新状态

**示例流程**：
```
[unilab-device-monitor] → [function: 解析状态] → [dashboard图表]
```

---

#### `unilab-device-list`
**类别**：UniLab
**颜色**：蓝色 (#4DA6FF)
**图标**：fa-list

**功能**：获取在线设备列表

**输入**：
- 任意消息（触发查询）

**输出**：
- `msg.payload`：设备列表
  ```json
  {
    "data": [
      {"id": "/PRCXI", "type": "liquid_handler", "status": "online"},
      {"id": "/Heater", "type": "heatchill", "status": "online"}
    ]
  }
  ```

**配置参数**：
- `backend`：后端配置节点

**示例流程**：
```
[inject: 每10秒] → [unilab-device-list] → [dashboard下拉框]
```

---

### 4. 操作节点

所有操作节点都有两种模式：

| 模式 | 功能 | 使用场景 |
|------|------|---------|
| **立即执行** | 收到消息后立即提交单个任务到 UniLab | 临时操作、测试 |
| **协议描述符** | 将节点参数打包为 `msg.payload` 传递给下游 | 构建协议流程 |

---

#### `unilab-transfer-liquid`
**类别**：UniLab操作
**颜色**：蓝色 (#3498DB)
**图标**：fa-tint

**功能**：液体转移操作

**配置参数**：
- `backend`：后端配置节点
- `device_id`：设备 ID
- `mode`：执行模式（execute / descriptor）
- `asp_vol`：吸液量（µL）
- `dis_vol`：分液量（µL）
- `sources`：来源孔位（如 "A1,A2,A3"）
- `targets`：目标孔位（如 "B1,B2,B3"）
- `liquid_class`：液体类型（可选）
- `mix_cycles`：混合次数（可选）

**输入**：
- 任意消息（触发执行）
- `msg.device_id`：覆盖节点配置的设备 ID
- `msg.asp_vol`：覆盖吸液量
- ...（其他参数同理）

**输出**：
- **立即执行模式**：
  ```json
  {
    "payload": {"id": "job1", "unilab_job_id": "..."},
    "jobId": "job1"
  }
  ```
- **协议描述符模式**：
  ```json
  {
    "payload": {
      "type": "unilab-transfer-liquid",
      "device_id": "/PRCXI",
      "action": "transfer_liquid",
      "action_args": {
        "asp_vol": 100,
        "dis_vol": 100,
        "sources": "A1,A2",
        "targets": "B1,B2"
      }
    }
  }
  ```

**示例流程（立即执行）**：
```
[inject] → [unilab-transfer-liquid] → [unilab-job-status] → [debug]
```

**示例流程（协议）**：
```
[inject] → [unilab-transfer-liquid] → [unilab-incubation] → [保存协议]
```

---

#### `unilab-incubation`
**类别**：UniLab操作
**颜色**：橙色 (#E67E22)
**图标**：fa-thermometer-half

**功能**：孵育操作

**配置参数**：
- `backend`：后端配置节点
- `device_id`：设备 ID
- `mode`：执行模式
- `duration`：持续时间（秒）
- `temperature`：温度（°C）
- `shaking_speed`：振荡速度（rpm，可选）

**示例**：
```json
{
  "device_id": "/Incubator",
  "duration": 3600,
  "temperature": 37,
  "shaking_speed": 200
}
```

---

#### `unilab-heat-chill`
**类别**：UniLab操作
**颜色**：红色 (#C0392B)
**图标**：fa-snowflake-o

**功能**：温控操作

**配置参数**：
- `backend`：后端配置节点
- `device_id`：设备 ID
- `mode`：执行模式
- `target_temp`：目标温度（°C）
- `hold_time`：保温时间（秒）
- `ramp_rate`：升降温速率（°C/s，可选）

**示例**：
```json
{
  "device_id": "/Heater",
  "target_temp": 80,
  "hold_time": 7200,
  "ramp_rate": 1.0
}
```

---

#### `unilab-move-labware`
**类别**：UniLab操作
**颜色**：绿色 (#27AE60)
**图标**：fa-exchange

**功能**：耗材移动操作

**配置参数**：
- `backend`：后端配置节点
- `device_id`：设备 ID
- `mode`：执行模式
- `source`：来源位置（如 "deck_1"）
- `target`：目标位置（如 "deck_2"）
- `labware_type`：耗材类型（如 "96_well_plate"）

**示例**：
```json
{
  "device_id": "/RobotArm",
  "source": "deck_1",
  "target": "incubator_slot_1",
  "labware_type": "96_well_plate"
}
```

---

## 安装方法

### 方法 1：本地安装（开发）

```bash
cd ~/.node-red
npm install /path/to/node-red-contrib-unilab
node-red
```

### 方法 2：从 npm 安装（未发布）

```bash
cd ~/.node-red
npm install node-red-contrib-unilab
node-red
```

### 验证安装

1. 打开 Node-RED：`http://localhost:1880`
2. 在左侧节点面板查找 "UniLab" 和 "UniLab操作" 分类
3. 应该看到 9 个节点

---

## 使用示例

### 示例 1：简单液体转移

```
[inject: 手动触发]
    ↓
[unilab-transfer-liquid]
  - mode: 立即执行
  - device_id: /PRCXI
  - asp_vol: 100
  - dis_vol: 100
  - sources: A1
  - targets: B1
    ↓
[unilab-job-status]
  - pollInterval: 5
    ↓ (输出1: 成功)
[debug: 显示结果]
```

---

### 示例 2：构建协议并保存

```
[inject: 触发]
    ↓
[unilab-transfer-liquid]
  - mode: 协议描述符
  - asp_vol: 100
  - sources: A1,A2,A3
  - targets: B1,B2,B3
    ↓
[unilab-incubation]
  - mode: 协��描述符
  - duration: 3600
  - temperature: 37
    ↓
[unilab-heat-chill]
  - mode: 协议描述符
  - target_temp: 80
  - hold_time: 7200
    ↓
[function: 收集所有节点]
  - 将所有 msg.payload 收集到数组
    ↓
[http request: POST /api/protocols]
  - 保存协议到数据库
    ↓
[debug: 显示协议 ID]
```

---

### 示例 3：实时监控 Dashboard

```
[unilab-device-monitor]
    ↓
[function: 解析设备状态]
  - 提取温度、状态等信息
    ↓
[dashboard: 仪表盘]
  - 显示实时温度曲线
  - 显示设备在线状态
```

---

### 示例 4：协议执行与监控

```
[dashboard: 按钮 "运行协议A"]
    ↓
[function: 设置 protocolId]
  - msg.protocolId = "protocol-abc-123"
    ↓
[unilab-submit-job]
    ↓
[unilab-job-status]
    ↓ (输出1: 成功)
[dashboard: 通知 "协议执行成功"]
    ↓ (输出2: 失败)
[dashboard: 通知 "协议执行失败"]
```

---

## 开发指南

### 添加新的操作节点

1. **创建节点文件**：
   ```bash
   cd node-red-contrib-unilab/nodes
   touch unilab-new-operation.js
   touch unilab-new-operation.html
   ```

2. **编写 JS 文件**（使用 operation-base 辅助函数）：
   ```javascript
   const makeOperationNode = require('./unilab-operation-base');
   module.exports = function (RED) {
     makeOperationNode(RED, 'unilab-new-operation', ['param1', 'param2']);
   };
   ```

3. **编写 HTML 文件**：
   ```html
   <script type="text/javascript">
     RED.nodes.registerType('unilab-new-operation', {
       category: 'UniLab操作',
       color: '#3498DB',
       defaults: {
         name: { value: '' },
         backend: { value: '', type: 'unilab-config' },
         device_id: { value: '' },
         mode: { value: 'execute' },
         param1: { value: 0 },
         param2: { value: '' }
       },
       inputs: 1,
       outputs: 1,
       icon: 'font-awesome/fa-cog',
       label: function () { return this.name || '新操作'; }
     });
   </script>

   <script type="text/html" data-template-name="unilab-new-operation">
     <!-- 配置界面 -->
   </script>
   ```

4. **注册节点**（在 `package.json`）：
   ```json
   {
     "node-red": {
       "nodes": {
         "unilab-new-operation": "nodes/unilab-new-operation.js"
       }
     }
   }
   ```

5. **重启 Node-RED**：
   ```bash
   node-red-stop
   node-red-start
   ```

---

## 故障排查

### 问题 1：节点不显示

**原因**：安装路径错误或 package.json 配置错误

**解决**：
```bash
cd ~/.node-red
npm list node-red-contrib-unilab  # 检查是否安装
cat node_modules/node-red-contrib-unilab/package.json  # 检查配置
```

---

### 问题 2：连接后端失败

**原因**：lab-backend 未启动或 URL 配置错误

**解决**：
1. 检查 lab-backend 是否运行：
   ```bash
   curl http://localhost:3000/health
   ```
2. 检查 unilab-config 节点的 URL 配置
3. 查看 Node-RED 日志：
   ```bash
   node-red-log
   ```

---

### 问题 3：WebSocket 断开

**原因**：lab-backend 重启或网络问题

**解决**：
- unilab-device-monitor 会自动重连（5 秒后）
- 检查 lab-backend 日志：
  ```bash
  tail -f lab-backend/logs/app.log
  ```

---

## 最佳实践

### 1. 使用配置节点

所有节点共享同一个 unilab-config 配置，避免重复配置 URL。

### 2. 协议描述符模式

构建复杂协议时，使用"协议描述符"模式，最后统一保存到数据库。

### 3. 错误处理

使用 unilab-job-status 的两个输出分别处理成功和失败情况。

### 4. 实时监控

使用 unilab-device-monitor + Node-RED Dashboard 构建实时监控界面。

### 5. 参数验证

在 function 节点中验证参数，避免提交无效任务。

---

## 参考资料

- [Node-RED 官方文档](https://nodered.org/docs/)
- [lab-backend API 文档](../api/lab-backend-api.md)
- [UniLab 支持的操作](../architecture/UNILAB_SUPPORTED_OPERATIONS.md)
