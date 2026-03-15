# UniLab 快速开始指南

> **目标**：5 分钟内启动 UniLab 系统并验证功能
> **难度**：⭐ 入门级

---

## 前置要求

### 系统要求
- **操作系统**：Windows 11 / Linux / macOS
- **Python**：3.8+
- **Conda/Mamba**：已安装（推荐 Mamba）
- **磁盘空间**：至少 5GB

### 可选组件
- **Node-RED**：用于可视化协议编辑（可选）
- **Node.js**：18+ (Node-RED 需要)

---

## 步骤 1：安装 UniLab

### 使用 Mamba（推荐）

```bash
# 创建环境
mamba create -n unilab python=3.10

# 激活环境
mamba activate unilab

# 安装 UniLab
cd /path/to/Uni-Lab-OS
pip install -e .

# 验证安装
unilab --version
```

### 使用 Conda

```bash
conda create -n unilab python=3.10
conda activate unilab
cd /path/to/Uni-Lab-OS
pip install -e .
```

---

## 步骤 2：准备设备连接图

### 使��示例配置（测试）

```bash
cd /path/to/Uni-Lab-OS

# 如果没有 devices.json，创建一个最小配置
cat > devices_test.json << 'EOF'
{
  "nodes": [
    {
      "id": "host_node",
      "type": "device",
      "name": "host_node"
    }
  ],
  "links": []
}
EOF
```

### 使用真实设备配置

如果你有真实设备，准备 `devices_graph.json`：
```json
{
  "nodes": [
    {
      "id": "/PRCXI",
      "type": "device",
      "class": "PRCXI_LiquidHandler",
      "config": {...}
    },
    {
      "id": "/PRCXI/Deck",
      "type": "resource",
      "parent": "/PRCXI"
    }
  ],
  "links": [...]
}
```

---

## 步骤 3：启动 UniLab（本地模式）

### 基本启动

```bash
mamba activate unilab

unilab --local_mode \
       --backend ros \
       --app_bridges fastapi \
       -g devices_test.json
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--local_mode` | 本地模式，跳过云端验证 | False |
| `--backend ros` | 使用 ROS2 后端 | ros |
| `--app_bridges fastapi` | 启用 FastAPI Web 服务 | websocket,fastapi |
| `-g devices_test.json` | 设备连接图文件 | 无 |

### 预期输出

```
🚀 UniLab-OS v0.10.18
✅ 启用本地模式：跳过云端验证
✅ 加载设备连接图: devices_test.json
✅ 启动 ROS2 后端
✅ 启动 FastAPI 服务: http://localhost:8002
✅ 系统就绪
```

---

## 步骤 4：验证 UniLab API

### 测试 1：健康检查

```bash
curl http://localhost:8002/health
```

**预期输出**：
```json
{"status": "ok"}
```

### 测试 2：获取在线设备

```bash
curl http://localhost:8002/api/v1/online-devices
```

**预期输出**：
```json
{
  "code": 0,
  "data": [
    {"id": "host_node", "type": "device", "status": "online"}
  ]
}
```

### 测试 3：提交测试任务

```bash
curl -X POST http://localhost:8002/api/v1/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "host_node",
    "action": "test_latency",
    "action_args": {}
  }'
```

**预期输出**：
```json
{
  "code": 0,
  "data": {
    "id": "job_xxx",
    "status": 1
  }
}
```

---

## 步骤 5：启动 lab-backend（可选）

如果需要使用 Node-RED 或 Web 前端：

```bash
# 新开一个终端
cd /path/to/Uni-Lab-OS/lab-backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### 验证 lab-backend

```bash
curl http://localhost:3000/health
```

**预期输出**：
```json
{"status": "ok"}
```

---

## 步骤 6：安装 Node-RED 节点（可选）

### 安装 Node-RED

```bash
npm install -g node-red
```

### 安装 UniLab 节点

```bash
cd ~/.node-red
npm install /path/to/Uni-Lab-OS/node-red-contrib-unilab
```

### 启动 Node-RED

```bash
node-red
```

访问：`http://localhost:1880`

### 验证节点

1. 在左侧节点面板查找 "UniLab" 分类
2. 应该看到 9 个自定义节点
3. 拖拽 `unilab-config` 到画布，配置后端 URL：`http://localhost:3000`

---

## 完整系统架构

启动后的系统架构：

```
┌─────────────────────────────────────┐
│  Node-RED (localhost:1880)          │  ← 可视化协议编辑器
│  - 9 个自定义节点                    │
└──────────────┬──────────────────────┘
               │ HTTP REST
┌──────────────▼──────────────────────┐
│  lab-backend (localhost:3000)       │  ← FastAPI 中间层
│  - 协议管理                          │
│  - 任务管理                          │
│  - WebSocket 代理                    │
└──────────────┬──────────────────────┘
               │ HTTP + WebSocket
┌──────────────▼──────────────────────┐
│  UniLab (localhost:8002)            │  ← ROS2 核心
│  - 设备控制                          │
│  - 工作流执行                        │
└──────────────┬──────────────────────┘
               │ 设备协议
┌──────────────▼──────────────────────┐
│  实验室设备                          │
└─────────────────────────────────────┘
```

---

## 常见问题

### Q1: 启动时提示 "后续运行必须拥有一个实验室"

**原因**：未使用 `--local_mode` 参数

**解决**：
```bash
unilab --local_mode ...
```

### Q2: 端口 8002 已被占用

**解决**：
```bash
# 方法 1：更改端口
unilab --local_mode --port 8003 ...

# 方法 2：杀死占用进程
lsof -ti:8002 | xargs kill -9  # Linux/macOS
netstat -ano | findstr :8002   # Windows
```

### Q3: 找不到 devices.json

**解决**：
```bash
# 使用绝对路径
unilab --local_mode -g /absolute/path/to/devices.json ...

# 或者在当前目录创建
touch devices_test.json
```

### Q4: ROS2 相关错误

**原因**：ROS2 环境未正确配置

**解决**：
```bash
# 检查 ROS2 是否安装
ros2 --version

# 如果未安装，使用 simple 后端
unilab --local_mode --backend simple ...
```

### Q5: lab-backend 连接失败

**检查清单**：
1. UniLab 是否在运行？`curl http://localhost:8002/health`
2. lab-backend 是否在运行？`curl http://localhost:3000/health`
3. 环境变量是否正确？`echo $UNILAB_URL`

---

## 下一步

### 学习路径

1. **理解架构**：阅读 [`EXPLORATION_GUIDE.md`](../EXPLORATION_GUIDE.md)
2. **查看操作**：浏览 [`architecture/UNILAB_SUPPORTED_OPERATIONS.md`](../architecture/UNILAB_SUPPORTED_OPERATIONS.md)
3. **开发协议**：使用 Node-RED 创建实验流程
4. **集成设备**：参考 [`guides/device-integration.md`](./device-integration.md)

### 示例任务

- **任务 1**：在 Node-RED 中创建一个简单的液体转移协议
- **任务 2**：通过 API 提交任务并查询状态
- **任务 3**：监控设备状态（WebSocket）
- **任务 4**：添加一个虚拟设备

---

## 获取帮助

### 文档资源
- 探索指南：[`EXPLORATION_GUIDE.md`](../EXPLORATION_GUIDE.md)
- 编译机制：[`architecture/UNILAB_COMPILATION_ANALYSIS.md`](../architecture/UNILAB_COMPILATION_ANALYSIS.md)
- API 文档：[`api/lab-backend-api.md`](../api/lab-backend-api.md)

### 故障排查
- 查看日志：`tail -f ~/.unilab/logs/unilab.log`
- 检查配置：`cat ~/.unilab/config.yaml`
- 重置环境：`rm -rf ~/.unilab && unilab --local_mode ...`

---

## 总结

你已经成功启动了 UniLab 系统！

**已完成**：
- ✅ 安装 UniLab
- ✅ 启动本地模式
- ✅ 验证 API 功能
- ✅ （可选）启动 lab-backend
- ✅ （可选）安装 Node-RED 节点

**下一步**：
- 📖 阅读 [`EXPLORATION_GUIDE.md`](../EXPLORATION_GUIDE.md) 深入了解系统
- 🧪 尝试提交真实的实验任务
- 🔧 集成你的实验室设备
