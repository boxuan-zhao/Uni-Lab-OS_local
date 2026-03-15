# UniLab-OS Claude 文档中心

> **文档版本**：v1.0
> **最后更新**：2026-03-15
> **维护者**：Claude AI Assistant

---

## 📚 文档结构

```
claudereadme/
├── README.md                           # 本文件（文档导航）
├── EXPLORATION_GUIDE.md                # 🌟 探索指南（从这里开始）
├── architecture/                       # 架构与编译机制
│   ├── UNILAB_COMPILATION_ANALYSIS.md  # 编译转化机制深度分析
│   └── UNILAB_SUPPORTED_OPERATIONS.md  # 支持的操作清单
├── api/                                # API 文档
│   ├── lab-backend-api.md              # FastAPI 中间层 API
│   └── node-red-nodes.md               # Node-RED 自定义节点说明
└── guides/                             # 操作指南
    ├── quick-start.md                  # 快速开始
    ├── local-mode-setup.md             # 本地模式配置
    └── device-integration.md           # 设备集成指南
```

---

## 🚀 快速开始

### 新手入门路径

1. **第一步**：阅读 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md)
   - 了解项目概述和核心架构
   - 学习 4 种探索方法论
   - 查看关键文件索引

2. **第二步**：根据你的目标选择文档

   | 你的目标 | 推荐文档 | 阅读时间 |
   |---------|---------|---------|
   | 理解 UniLab 如何工作 | [`architecture/UNILAB_COMPILATION_ANALYSIS.md`](./architecture/UNILAB_COMPILATION_ANALYSIS.md) | 30 分钟 |
   | 查询支持的操作 | [`architecture/UNILAB_SUPPORTED_OPERATIONS.md`](./architecture/UNILAB_SUPPORTED_OPERATIONS.md) | 15 分钟 |
   | 开发 Web 应用 | [`api/lab-backend-api.md`](./api/lab-backend-api.md) | 20 分钟 |
   | 使用 Node-RED | [`api/node-red-nodes.md`](./api/node-red-nodes.md) | 15 分钟 |
   | 配置本地环境 | [`guides/local-mode-setup.md`](./guides/local-mode-setup.md) | 10 分钟 |

3. **第三步**：动手实践
   - 参考 [`guides/quick-start.md`](./guides/quick-start.md) 启动系统
   - 使用 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md) 的"常见任务指南"完成具体任务

---

## 📖 文档详解

### 核心文档

#### 🌟 [EXPLORATION_GUIDE.md](./EXPLORATION_GUIDE.md)
**最重要的文档，从这里开始！**

**内容**：
- 项目概述与系统架构
- 已导出文档的使用说明
- 关键文件索引（50+ 个文件）
- 4 种探索方法论
- 10+ 个常见任务的操作步骤
- 扩展开发指南
- 故障排查清单

**适合**：
- ✅ 新接手项目的开发者
- ✅ 需要快速定位代码的 Agent
- ✅ 想要理解整体架构的人

---

### 架构文档

#### [architecture/UNILAB_COMPILATION_ANALYSIS.md](./architecture/UNILAB_COMPILATION_ANALYSIS.md)
**深入理解 UniLab 的编译机制**

**内容**：
- 三层编译架构详解
  - 第一层：化学协议 → 设备操作
  - 第二层：设备操作 → PyLabRobot 原语
  - 第三层：PyLabRobot 原语 → 硬件指令
- 设备连接图在每层的作用
- 完整编译链路示例（XDL → 泵阀指令）
- 代码位置索引（精确到行号）

**适合**：
- ✅ 需要理解编译流程的开发者
- ✅ 开发新的工作流编译器
- ✅ 调试编译错误
- ✅ 优化编译性能

**关键洞察**：
- 设备连接图是编译的核心依赖
- 一个 `transfer_liquid` 操作可能生成 50+ 个硬件指令
- 编译复杂度与设备类型相关

---

#### [architecture/UNILAB_SUPPORTED_OPERATIONS.md](./architecture/UNILAB_SUPPORTED_OPERATIONS.md)
**UniLab 支持的所有操作参考手册**

**内容**：
- 7 大类操作清单
  1. 液体处理操作（17 个）
  2. 温度控制操作（8 个）
  3. 机械臂与移动操作（7 个）
  4. 泵阀操作（10 个）
  5. 分析仪器操作
  6. 有机合成操作（6 个）
  7. 工作站操作
- 每个操作的参数说明
- 编译复杂度对比
- 操作示例（输入 → 输出）

**适合**：
- ✅ 查询 UniLab 是否支持某个操作
- ✅ 了解操作的参数格式
- ✅ 评估新操作的开发难度
- ✅ 编写工作流时的参考

**快速查找**：
```bash
# 查询是否支持某个操作
grep "transfer_liquid" architecture/UNILAB_SUPPORTED_OPERATIONS.md

# 查看所有液体处理操作
grep "^| \*\*" architecture/UNILAB_SUPPORTED_OPERATIONS.md | head -20
```

---

### API 文档

#### [api/lab-backend-api.md](./api/lab-backend-api.md)
**FastAPI 中间层 API 文档**

**内容**：
- REST API 端点列表
  - 协议管理（CRUD）
  - 任务管理（提交、查询、历史）
  - 设备代理（转发 UniLab API）
- WebSocket 端点
  - 实时设备状态流
- 数据库设计（SQLite）
- 格式转换器（Node-RED flow → UniLab job）
- 启动命令

**适合**：
- ✅ 开发 Web 前端
- ✅ 集成 Node-RED
- ✅ 扩展 API 功能
- ✅ 理解中间层架构

**快速启动**：
```bash
cd lab-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

---

#### [api/node-red-nodes.md](./api/node-red-nodes.md)
**Node-RED 自定义节点说明**

**内容**：
- 9 个自定义节点的功能
  - 配置节点：unilab-config
  - 控制节点：unilab-submit-job, unilab-job-status
  - 监控节点：unilab-device-monitor, unilab-device-list
  - 操作节点：unilab-transfer-liquid, unilab-incubation, unilab-heat-chill, unilab-move-labware
- 节点参数说明
- 使用示例
- 安装方法

**适合**：
- ✅ 使用 Node-RED 编辑实验协议
- ✅ 开发新的 Node-RED 节点
- ✅ 集成 Node-RED Dashboard

**快速安装**：
```bash
cd ~/.node-red
npm install /path/to/node-red-contrib-unilab
node-red
```

---

### 操作指南

#### [guides/quick-start.md](./guides/quick-start.md)
**5 分钟快速启动 UniLab 系统**

**内容**：
- 环境要求
- 安装步骤
- 启动命令
- 验证方法
- 常见问题

**适合**：
- ✅ 第一次使用 UniLab
- ✅ 快速搭建测试环境

---

#### [guides/local-mode-setup.md](./guides/local-mode-setup.md)
**配置 UniLab 本地模式（无云端依赖）**

**内容**：
- 本地模式的作用
- 配置步骤
- 启动命令
- 与云端模式的区别
- 故障排查

**适合**：
- ✅ 离线环境部署
- ✅ 开发测试环境
- ✅ 不想注册云端账号

**关键命令**：
```bash
unilab --local_mode --backend ros --app_bridges fastapi -g devices.json
```

---

#### [guides/device-integration.md](./guides/device-integration.md)
**集成新设备的完整指南**

**内容**：
- 添加新设备的 5 个步骤
- 设备驱动开发模板
- Registry YAML 配置
- 测试方法
- 最佳实践

**适合**：
- ✅ 添加新设备支持
- ✅ 开发自定义设备驱动
- ✅ 扩展 UniLab 功能

---

## 🔍 文档使用场景

### 场景 1：我是新手，想快速了解 UniLab

**路径**：
1. 阅读 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md) 的"项目概述"和"核心架构"（10 分钟）
2. 浏览 [`architecture/UNILAB_SUPPORTED_OPERATIONS.md`](./architecture/UNILAB_SUPPORTED_OPERATIONS.md) 了解功能（10 分钟）
3. 跟随 [`guides/quick-start.md`](./guides/quick-start.md) 启动系统（5 分钟）

**总时间**：25 分钟

---

### 场景 2：我想理解某个功能如何实现

**路径**：
1. 在 [`architecture/UNILAB_SUPPORTED_OPERATIONS.md`](./architecture/UNILAB_SUPPORTED_OPERATIONS.md) 查询操作是否支持
2. 在 [`architecture/UNILAB_COMPILATION_ANALYSIS.md`](./architecture/UNILAB_COMPILATION_ANALYSIS.md) 查看编译流程
3. 在 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md) 的"关键文件索引"找到源码位置
4. 使用"探索方法论"定位代码

**工具**：
```bash
# 快速搜索
grep -r "transfer_liquid" claudereadme/
```

---

### 场景 3：我想开发 Web 应用对接 UniLab

**路径**：
1. 阅读 [`api/lab-backend-api.md`](./api/lab-backend-api.md) 了解 API（15 分钟）
2. 启动 lab-backend 服务（5 分钟）
3. 使用 Postman/curl 测试 API（10 分钟）
4. 参考 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md) 的"常见任务指南"完成具体功能

**示例代码**：
```python
import httpx

async def submit_protocol(protocol_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:3000/api/jobs/submit",
            json={"protocol_id": protocol_id}
        )
        return r.json()
```

---

### 场景 4：我想添加新设备

**路径**：
1. 阅读 [`guides/device-integration.md`](./guides/device-integration.md)（20 分钟）
2. 参考 [`architecture/UNILAB_SUPPORTED_OPERATIONS.md`](./architecture/UNILAB_SUPPORTED_OPERATIONS.md) 中类似设备的实现
3. 使用 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md) 的"扩展开发指南"
4. 按照 5 步流程实现

**检查清单**：
- [ ] 创建设备驱动类
- [ ] 编写 Registry YAML
- [ ] 更新设备连接图
- [ ] 编写测试用例
- [ ] 验证编译流程

---

### 场景 5：我遇到了错误，需要调试

**路径**：
1. 查看 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md) 的"故障排查清单"
2. 根据错误类型定位问题层级：
   - 编译错误 → [`architecture/UNILAB_COMPILATION_ANALYSIS.md`](./architecture/UNILAB_COMPILATION_ANALYSIS.md)
   - API 错误 → [`api/lab-backend-api.md`](./api/lab-backend-api.md)
   - 设备错误 → [`guides/device-integration.md`](./guides/device-integration.md)
3. 使用"探索方法论"定位源码
4. 查看日志文件

**调试技巧**：
```bash
# 查看 UniLab 日志
tail -f ~/unilabos_data/logs/unilab.log

# 查看 lab-backend 日志
uvicorn main:app --log-level debug

# 测试单个操作
python -c "from unilabos.devices.liquid_handling import ...; ..."
```

---

## 📊 文档关系图

```
EXPLORATION_GUIDE.md (入口)
    ├── 引用 → architecture/UNILAB_COMPILATION_ANALYSIS.md
    ├── 引用 → architecture/UNILAB_SUPPORTED_OPERATIONS.md
    ├── 引用 → api/lab-backend-api.md
    └── 引用 → guides/*.md

architecture/UNILAB_COMPILATION_ANALYSIS.md
    ├── 依赖 → architecture/UNILAB_SUPPORTED_OPERATIONS.md (操作定义)
    └── 被引用 ← EXPLORATION_GUIDE.md

architecture/UNILAB_SUPPORTED_OPERATIONS.md
    ├── 被引用 ← EXPLORATION_GUIDE.md
    ├── 被引用 ← architecture/UNILAB_COMPILATION_ANALYSIS.md
    └── 被引用 ← guides/device-integration.md

api/lab-backend-api.md
    ├── 依赖 → architecture/UNILAB_SUPPORTED_OPERATIONS.md (操作格式)
    ├── 被引用 ← EXPLORATION_GUIDE.md
    └── 被引用 ← api/node-red-nodes.md

api/node-red-nodes.md
    ├── 依赖 → api/lab-backend-api.md (API 端点)
    └── 被引用 ← EXPLORATION_GUIDE.md

guides/*.md
    ├── 依赖 → EXPLORATION_GUIDE.md (架构理解)
    └── 被引用 ← EXPLORATION_GUIDE.md
```

---

## 🛠️ 文档维护

### 更新规则

| 变化类型 | 需要更新的文档 |
|---------|---------------|
| 添加新设备 | `architecture/UNILAB_SUPPORTED_OPERATIONS.md`, `EXPLORATION_GUIDE.md` (关键文件索引), `guides/device-integration.md` (示例) |
| 修改编译流程 | `architecture/UNILAB_COMPILATION_ANALYSIS.md` |
| 添加新 API | `api/lab-backend-api.md` |
| 修改配置参数 | `EXPLORATION_GUIDE.md` (配置与启动), `guides/local-mode-setup.md` |
| 添加新功能 | `EXPLORATION_GUIDE.md` (常见任务指南), 相关 `guides/*.md` |

### 文档版本

- **v1.0** (2026-03-15)：初始版本
  - 完成核心架构文档
  - 完成 API 文档
  - 完成探索指南

---

## 💡 给 Agent 的提示

### 使用这些文档时

1. **从 EXPLORATION_GUIDE.md 开始**：它是所有文档的索引
2. **使用搜索**：`grep -r "关键词" claudereadme/` 快速定位
3. **关注代码位置**：文档中标注了精确的文件路径和行号
4. **理解层次关系**：架构 → API → 指南，从宏观到微观
5. **实践验证**：文档中的命令都可以直接运行

### 探索 UniLab 源码时

1. **先查文档**：避免盲目搜索，节省时间
2. **使用文件索引**：EXPLORATION_GUIDE.md 的"关键文件索引"列出了 50+ 个关键文件
3. **跟随数据流**：理解数据如何从输入流向输出
4. **查看测试用例**：`unilabos/devices/*/test_*.py` 是最好的示例
5. **参考虚拟设备**：`unilabos/devices/virtual/*.py` 是简化的实现

---

## 📞 获取帮助

### 文档问题
- 文档不清楚？在 EXPLORATION_GUIDE.md 查看"故障排查清单"
- 找不到信息？使用 `grep -r "关键词" claudereadme/`
- 需要更多示例？查看 `unilabos/devices/*/test_*.py`

### 代码问题
- 编译错误？查看 `architecture/UNILAB_COMPILATION_ANALYSIS.md`
- API 错误？查看 `api/lab-backend-api.md`
- 设备错误？查看 `guides/device-integration.md`

---

## 🎯 下一步

1. **立即开始**：打开 [`EXPLORATION_GUIDE.md`](./EXPLORATION_GUIDE.md)
2. **选择路径**：根据你的目标选择相应文档
3. **动手实践**：跟随 [`guides/quick-start.md`](./guides/quick-start.md) 启动系统
4. **深入学习**：阅读架构文档理解原理
5. **扩展开发**：参考指南添加新功能

**祝你探索愉快！** 🚀
