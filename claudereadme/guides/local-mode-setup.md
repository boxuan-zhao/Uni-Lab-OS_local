# UniLab 本地模式配置指南

> **目标**：配置 UniLab 在无云端依赖的环境下运行
> **难度**：⭐⭐ 中级

---

## 什么是本地模式？

### 云端模式 vs 本地模式

| 特性 | ���端模式 | 本地模式 |
|------|---------|---------|
| **需要注册** | ✅ 需要 ak/sk | ❌ 不需要 |
| **网络依赖** | ✅ 需要联网 | ❌ 完全离线 |
| **数据上传** | ✅ 上传到云端 | ❌ 仅本地存储 |
| **设备同步** | ✅ 云端同步 | ❌ 本地管理 |
| **适用场景** | 多实验室协作 | 单机/离线环境 |

### 本地模式的优势

1. **隐私保护**：实验数据不离开本地
2. **离线运行**：无需互联网连接
3. **快速部署**：无需注册账号
4. **开发测试**：适合开发和调试

---

## 实现原理

### 代码修改位置

本地模式通过修改 UniLab 核心代码实现，涉及 2 个文件：

#### 1. `unilabos/config/config.py`

**修改内容**：添加 `local_mode` 配置字段

```python
# Line 27
class BasicConfig:
    ak = ""
    sk = ""
    # ... 其他字段 ...
    local_mode = False  # 本地模式，跳过云端验证和同步
```

#### 2. `unilabos/app/main.py`

**修改内容 A**：添加 `--local_mode` CLI 参数

```python
# Line 174-180
parser.add_argument(
    "--local_mode",
    action="store_true",
    default=False,
    help="Local mode: skip cloud authentication and sync, run fully offline",
)
```

**修改内容 B**：设置配置值

```python
# Line 360-362
BasicConfig.local_mode = args_dict.get("local_mode", False)
if BasicConfig.local_mode:
    print_status("启用本地模式：跳过云端验证和同步", "info")
```

**修改内容 C**：跳过 ak/sk 验证

```python
# Line 415-420 (原 415-417)
if BasicConfig.local_mode:
    print_status("运行在本地模式，跳过云端验证", "info")
elif not BasicConfig.ak or not BasicConfig.sk:
    print_status("后续运行必须拥有一个实验室，请前往 https://uni-lab.bohrium.com 注册实验室！", "warning")
    os._exit(1)
```

---

## 配置步骤

### 步骤 1：验证代码修改

检查修改是否已应用：

```bash
cd /path/to/Uni-Lab-OS

# 检查 config.py
grep "local_mode" unilabos/config/config.py

# 检查 main.py
grep -A 2 "local_mode" unilabos/app/main.py | head -20
```

**预期输出**：
```
unilabos/config/config.py:    local_mode = False  # 本地模式，跳过云端验证和同步
unilabos/app/main.py:    "--local_mode",
unilabos/app/main.py:    BasicConfig.local_mode = args_dict.get("local_mode", False)
unilabos/app/main.py:    if BasicConfig.local_mode:
```

### 步骤 2：准备本地配置文件

创建 `local_config.py`（可选，用于持久化配置）：

```python
# local_config.py
class BasicConfig:
    ak = ""
    sk = ""
    local_mode = True
    working_dir = "./lab_data"
    upload_registry = False
    port = 8002
    log_level = "INFO"
```

### 步骤 3：准备设备连接图

创建最小设备图（测试用）：

```bash
cat > devices_local.json << 'EOF'
{
  "nodes": [
    {
      "id": "host_node",
      "type": "device",
      "name": "host_node",
      "class": "HostNode"
    }
  ],
  "links": []
}
EOF
```

或使用真实设备图：

```json
{
  "nodes": [
    {
      "id": "/PRCXI",
      "type": "device",
      "class": "PRCXI_LiquidHandler",
      "config": {
        "port": "COM3",
        "backend": "PRCXIBackend"
      }
    },
    {
      "id": "/PRCXI/Deck",
      "type": "resource",
      "parent": "/PRCXI",
      "class": "Deck"
    },
    {
      "id": "/PRCXI/Deck/T1",
      "type": "resource_holder",
      "parent": "/PRCXI/Deck",
      "position": {"x": 0, "y": 0, "z": 0}
    }
  ],
  "links": []
}
```

---

## 启动命令

### 基本启动（推荐）

```bash
mamba activate unilab

unilab --local_mode \
       --backend ros \
       --app_bridges fastapi \
       -g devices_local.json
```

### 使用配置文件启动

```bash
unilab --local_mode \
       --config local_config.py \
       --backend ros \
       --app_bridges fastapi \
       -g devices_local.json
```

### 完整参数示例

```bash
unilab --local_mode \
       --backend ros \
       --app_bridges fastapi \
       --port 8002 \
       --working_dir ./lab_data \
       --disable_browser \
       -g devices_local.json
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--local_mode` | **启用本地模式** | False |
| `--backend ros` | 后端类型（ros/simple） | ros |
| `--app_bridges fastapi` | 启用的桥接（websocket/fastapi） | websocket,fastapi |
| `-g devices_local.json` | 设备连接图文件 | 无（必需） |
| `--config local_config.py` | 配置文件路径 | 无 |
| `--port 8002` | Web 服务端口 | 8002 |
| `--working_dir ./lab_data` | 工作目录 | 当前目录/unilabos_data |
| `--disable_browser` | 禁止自动打开浏览器 | False |

---

## 验证本地模式

### 检查 1：启动日志

启动时应该看到：

```
✅ 启用本地模式：跳过云端验证和同步
✅ 运行在本地模式，跳过云端验证
```

### 检查 2：API 可用性

```bash
# 健康检查
curl http://localhost:8002/health

# 获取设备列表（应该返回本地设备）
curl http://localhost:8002/api/v1/online-devices

# 提交测试任务
curl -X POST http://localhost:8002/api/v1/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "host_node",
    "action": "test_latency",
    "action_args": {}
  }'
```

### 检查 3：无云端通信

使用网络监控工具验证没有外部连接：

```bash
# Linux/macOS
sudo tcpdump -i any host uni-lab.bohrium.com

# 应该没有任何输出（表示没有连接云端）
```

---

## 本地模式下的功能

### ✅ 可用功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 设备控制 | ✅ | 完全可用 |
| 任务提交 | ✅ | 本地执行 |
| 任务查询 | ✅ | 本地数据库 |
| WebSocket 状态推送 | ✅ | 本地推送 |
| 工作流执行 | ✅ | 本地编译和执行 |
| FastAPI Web 服务 | ✅ | 完全可用 |
| ���备注册表 | ✅ | 本地加载 |
| 资源管理 | ✅ | 本地管理 |

### ❌ 不可用功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 云端同步 | ❌ | 需要 ak/sk |
| 多实验室协作 | ❌ | 需要云端 |
| 远程监控 | ❌ | 需要云端 |
| 数据备份到云端 | ❌ | 仅本地存储 |
| 云端工作流库 | ❌ | 需要云端 |

---

## 与云端模式的区别

### 数据存储

**云端模式**：
```
本地数据 → 云端同步 → 多实验室共享
```

**本地模式**：
```
本地数据 → 仅本地存储 → 无同步
```

### 认证流程

**云端模式**：
```
启动 → 验证 ak/sk → 连接云端 → 同步设备 → 就绪
```

**本地模式**：
```
启动 → 跳过验证 → 加载本地设备 → 就绪
```

### API 行为

**云端模式**：
- `/api/v1/online-devices` → 返回云端同步的设备
- `/api/v1/job/add` → 提交到云端队列
- `/api/v1/job/{id}/status` → 查询云端状态

**本地模式**：
- `/api/v1/online-devices` → 返回本地设备
- `/api/v1/job/add` → 本地执行
- `/api/v1/job/{id}/status` → 查询本地状态

---

## 故障排查

### 问题 1：仍然提示需要 ak/sk

**症状**：
```
后续运行必须拥有一个实验室，请前往 https://uni-lab.bohrium.com 注册实验室！
```

**原因**：未使用 `--local_mode` 参数

**解决**：
```bash
# 确保添加 --local_mode
unilab --local_mode ...
```

### 问题 2：代码修改未生效

**症状**：添加 `--local_mode` 后仍然报错

**原因**：代码未正确修改或未重新安装

**解决**：
```bash
# 重新安装
cd /path/to/Uni-Lab-OS
pip install -e . --force-reinstall

# 验证修改
grep -n "local_mode" unilabos/app/main.py
```

### 问题 3：设备连接图加载失败

**症状**：
```
未指定设备加载文件路径
```

**原因**：未提供 `-g` 参数

**解决**：
```bash
# 使用绝对路径
unilab --local_mode -g /absolute/path/to/devices.json ...
```

### 问题 4：工作目录权限错误

**症状**：
```
Permission denied: './lab_data'
```

**解决**：
```bash
# 创建工作目录
mkdir -p ./lab_data
chmod 755 ./lab_data

# 或指定其他目录
unilab --local_mode --working_dir ~/unilab_data ...
```

---

## 高级配置

### 环境变量配置

除了命令行参数，还可以使用环境变量：

```bash
# 设置环境变量
export UNILABOS_BASICCONFIG_LOCAL_MODE=true
export UNILABOS_BASICCONFIG_PORT=8002
export UNILABOS_BASICCONFIG_WORKING_DIR=./lab_data

# 启动（无需 --local_mode 参数）
unilab --backend ros -g devices.json
```

### 配置文件优先级

```
命令行参数 > 环境变量 > 配置文件 > 默认值
```

示例：
```bash
# 配置文件中 local_mode = False
# 环境变量 UNILABOS_BASICCONFIG_LOCAL_MODE=true
# 命令行 --local_mode

# 最终结果：local_mode = True（命令行优先级最高）
```

---

## 生产环境部署

### 推荐配置

```bash
# 创建专用工作目录
mkdir -p /opt/unilab/data
mkdir -p /opt/unilab/logs

# 创建配置文件
cat > /opt/unilab/local_config.py << 'EOF'
class BasicConfig:
    local_mode = True
    working_dir = "/opt/unilab/data"
    port = 8002
    log_level = "INFO"
    disable_browser = True
EOF

# 启动服务
unilab --local_mode \
       --config /opt/unilab/local_config.py \
       --backend ros \
       --app_bridges fastapi \
       -g /opt/unilab/devices.json \
       > /opt/unilab/logs/unilab.log 2>&1 &
```

### 使用 systemd 管理（Linux）

```ini
# /etc/systemd/system/unilab.service
[Unit]
Description=UniLab Local Service
After=network.target

[Service]
Type=simple
User=unilab
WorkingDirectory=/opt/unilab
ExecStart=/opt/conda/envs/unilab/bin/unilab \
    --local_mode \
    --config /opt/unilab/local_config.py \
    --backend ros \
    --app_bridges fastapi \
    -g /opt/unilab/devices.json
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable unilab
sudo systemctl start unilab
sudo systemctl status unilab
```

---

## 总结

### 本地模式的关键点

1. **必须使用 `--local_mode` 参数**
2. **必须提供设备连接图 `-g`**
3. **无需 ak/sk 认证**
4. **数据仅存储在本地**
5. **完全离线运行**

### 下一步

- 📖 阅读 [`quick-start.md`](./quick-start.md) 了解基本操作
- 🔧 参考 [`device-integration.md`](./device-integration.md) 集成设备
- 🌐 查看 [`../api/lab-backend-api.md`](../api/lab-backend-api.md) 开发 Web 应用

---

## 参考资料

- 代码修改位置：
  - `unilabos/config/config.py:27`
  - `unilabos/app/main.py:174-180, 360-362, 415-420`
- 相关文档：
  - [`EXPLORATION_GUIDE.md`](../EXPLORATION_GUIDE.md)
  - [`architecture/UNILAB_COMPILATION_ANALYSIS.md`](../architecture/UNILAB_COMPILATION_ANALYSIS.md)
