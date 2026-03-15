# UniLab 内核支持的编译操作完整清单

## 概述

UniLab 通过 **设备注册表（Registry）** 系统支持多种实验室设备的操作编译。每个设备类型在 `unilabos/registry/devices/*.yaml` 中定义其支持的操作（actions）。

---

## 一、液体处理操作（Liquid Handling）

### 设备类型
- `liquid_handler.prcxi` — PRCXI 液体处理器
- `liquid_handler.biomek` — Biomek 液体处理器
- `liquid_handler.laiyu` — Laiyu 液体处理器

### 支持的操作

| 操作名称 | 功能描述 | 关键参数 |
|---------|---------|---------|
| **transfer_liquid** | 液体转移（核心操作） | sources, targets, asp_vols, dis_vols, asp_flow_rates, dis_flow_rates |
| **add_liquid** | 添加液体（试剂添加） | reagent_sources, targets, asp_vols, dis_vols, mix_time, mix_vol |
| **remove_liquid** | 移除液体 | sources, vols, waste_liquid |
| **aspirate** | 吸液 | resources, vols, use_channels, flow_rates, offsets |
| **dispense** | 分液 | resources, vols, use_channels, flow_rates, offsets |
| **mix** | 混合 | targets, mix_time, mix_vol, mix_rate, height_to_bottom |
| **stamp** | 印章��转移（96孔板） | source, target, volume, aspiration_flow_rate, dispense_flow_rate |
| **pick_up_tips** | 拾取吸头 | tip_spots, use_channels, offsets |
| **drop_tips** | 丢弃吸头 | tip_spots, use_channels, offsets |
| **discard_tips** | 废弃吸头到垃圾桶 | use_channels, offsets |
| **return_tips** | 归还吸头 | use_channels |
| **set_liquid** | 设置孔位液体信息 | wells, liquid_names, volumes |
| **set_liquid_from_plate** | 从板设置液体 | plate, well_names, liquid_names, volumes |
| **move_lid** | 移动盖子 | lid, to, intermediate_locations |
| **move_plate** | 移动板 | plate, to |
| **move_resource** | 移动资源 | resource, to, pickup_offset, destination_offset |
| **move_to** | 移动到指定位置 | well, dis_to_top, channel |

### 编译示例

**输入（化学指令）**:
```json
{
  "action": "transfer_liquid",
  "sources": "reagent_A",
  "targets": "reaction_vessel",
  "asp_vol": 100.0,
  "dis_vol": 100.0
}
```

**编译输出（PyLabRobot 原语序列）**:
```python
pick_up_tips([TipSpot("TipRack_1/A1")])
aspirate([Well("Deck/T4/A1")], [100.0], flow_rate=50)
dispense([Well("Deck/T1/B1")], [100.0], flow_rate=50)
discard_tips()
```

**硬件指令（PRCXI 驱动）**:
```python
move_xyz(x=300, y=0, z=50)
move_z(z=10)
pump_aspirate(volume=100, rate=50)
move_z(z=50)
move_xyz(x=0, y=0, z=50)
move_z(z=10)
pump_dispense(volume=100, rate=50)
```

---

## 二、温度控制操作（Temperature Control）

### 设备类型
- `temperature.heatchill` — 加热/冷却设备
- `temperature.incubator` — 孵育箱
- `temperature.shaker` — 振荡器

### 支持的操作

| 操作名称 | 功能描述 | 关键参数 |
|---------|---------|---------|
| **heat_chill** | 加热/冷却 | temp, time, stir, stir_speed, purpose, vessel |
| **heat_chill_start** | 开始加热/冷却 | temp, stir_speed |
| **heat_chill_stop** | 停止加热/冷却 | - |
| **incubation** | 孵育 | duration, temperature, shaking_speed |
| **oscillation** | 振荡 | speed, duration |
| **stir** | 搅拌 | speed, duration |
| **start_stir** | 开始搅拌 | speed |
| **stop_stir** | 停止搅拌 | - |

### 编译示例

**输入**:
```json
{
  "action": "heat_chill",
  "temp": 80,
  "time": 7200,
  "stir": true,
  "stir_speed": 300
}
```

**编译输出**:
```python
# 虚拟设备模拟
set_temperature(80)
set_stir_speed(300)
wait_for_temperature()
sleep(7200)
stop_stir()
```

**硬件指令（实际设备）**:
```python
# Modbus/OPC-UA 指令
write_register(TEMP_SETPOINT, 80)
write_register(STIR_SPEED, 300)
write_coil(HEATER_ON, True)
write_coil(STIRRER_ON, True)
# 等待 7200 秒
write_coil(HEATER_ON, False)
write_coil(STIRRER_ON, False)
```

---

## 三、机械臂与移动操作（Robotics）

### 设备类型
- `robot_arm` — 机械臂（Elite Robot, UR）
- `robot_gripper` — 夹爪（Robotiq）
- `robot_agv` — AGV 导航
- `robot_linear_motion` — 直线运动模块

### 支持的操作

| 操作名称 | 功能描述 | 关键参数 |
|---------|---------|---------|
| **move_labware** | 移动耗材 | source, target, labware_type |
| **pick_up_resource** | 拾取资源 | resource, offset, pickup_distance_from_top |
| **drop_resource** | 放下资源 | destination, offset |
| **move_picked_up_resource** | 移动已拾取资源 | to, offset |
| **grasp** | 夹取 | position, force |
| **release** | 释放 | - |
| **navigate_to** | 导航到位置 | x, y, theta |

---

## 四、泵阀操作（Pump & Valve）

### 设备类型
- `pump_and_valve.transfer_pump` — 转移泵
- `pump_and_valve.vacuum_pump` — 真空泵
- `pump_and_valve.solenoid_valve` — 电磁阀
- `pump_and_valve.multiway_valve` — 多通阀

### 支持的操作

| 操作名称 | 功能描述 | 关键参数 |
|---------|---------|---------|
| **pump_aspirate** | 泵吸液 | volume, rate |
| **pump_dispense** | 泵分液 | volume, rate |
| **pump_initialize** | 泵初始化 | - |
| **set_valve_position** | 设置阀门位置 | position |
| **valve_open_cmd** | 打开阀门 | valve_id |
| **open** | 打开 | - |
| **close** | 关闭 | - |
| **fill_syringe** | 填充注射器 | volume |
| **empty_syringe** | 清空注射器 | - |

---

## 五、分析仪器操作（Analytical Instruments）

### 5.1 色谱质谱（Chromatography & Mass Spectrometry）

**设备类型**: `zhida_gcms`, `characterization_chromatic`

| 操作名称 | 功能描述 |
|---------|---------|
| **execute_command_from_outer** | 执行外部命令 |
| **get_methods** | 获取分析方法 |
| **abort** | 中止分析 |
| **could_run** | 检查是否可运行 |

### 5.2 光谱分析（Spectroscopy）

**设备类型**: `opsky_ATR30007` (Raman), `characterization_optic`

| 操作名称 | 功能描述 |
|---------|---------|
| **raman_cmd** | 拉曼光谱命令 |

### 5.3 核磁共振（NMR）

**设备类型**: `Qone_nmr`

| 操作名称 | 功能描述 |
|---------|---------|
| **start** | 开始测量 |
| **abort** | 中止测量 |
| **get_status** | 获取状态 |

### 5.4 X射线衍射（XRD）

**设备类型**: `xrd_d7mate`

---

## 六、有机合成操作（Organic Synthesis）

### 设备类型
- `organic_miscellaneous.rotavap` — 旋转蒸发仪
- `organic_miscellaneous.filter` — 过滤器
- `organic_miscellaneous.separator` — 分液器
- `organic_miscellaneous.column` — 色谱柱

### 支持的操作

| 操作名称 | 功能描述 | 关键参数 |
|---------|---------|---------|
| **evaporate** | 蒸发 | temperature, pressure, time |
| **filter** | 过滤 | filter_type, flow_rate |
| **separate** | 分液 | phases |
| **run_column** | 色谱分离 | solvent, flow_rate |
| **motor_rotate_quarter** | 电机旋转1/4圈 | - |
| **motor_run_continuous** | 电机连续运行 | speed |
| **motor_stop** | 电机停止 | - |
| **sensor_level** | 液位传感器 | - |

---

## 七、工作站操作（Workstation）

### 设备类型
- `work_station` — 通用工作站
- `coin_cell_workstation` — 扣式电池工作站
- `bioyond_dispensing_station` — 分液工作站
- `post_process_station` — 后处理工作站

### 支持的操作

| 操作名称 | 功能描述 |
|---------|---------|
| **batch_create_diamine_solution_tasks** | 批量创建二胺溶液任务 |
| **compute_experiment_design** | 计算实验设计 |
| **scheduler_start** | 启动调度器 |
| **trigger_post_processing** | 触发后处理 |
| **trigger_cleaning_action** | 触发清洁动作 |
| **trigger_grab_action** | 触发抓取动作 |

---

## 八、电池测试操作（Battery Testing）

### 设备类型
- `neware_battery_test_system` — Neware 电池测试系统

### 支持的操作

| 操作名称 | 功能描述 |
|---------|---------|
| **channel_status** | 通道状态 |
| **get_device_summary** | 获取设备摘要 |
| **get_plate_status** | 获取板状态 |
| **query_plate_action** | 查询板动作 |
| **export_status_json** | 导出状态JSON |

---

## 九、其他设备操作

### 9.1 天平（Balance）
**设备类型**: `balance`

### 9.2 相机（Camera）
**设备类型**: `camera`, `cameraSII`

### 9.3 固体分配器（Solid Dispenser）
**设备类型**: `solid_dispenser`

| 操作名称 | 功能描述 |
|---------|---------|
| **add_solid** | 添加固体 |
| **test_solid_dispenser** | 测试固体分配器 |

### 9.4 离心机（Centrifuge）
**设备类型**: `virtual.centrifuge`

| 操作名称 | 功能描述 |
|---------|---------|
| **centrifuge** | 离心 |

### 9.5 封口机（Sealer）
**设备类型**: `sealer`

---

## 十、编译操作的层级关系

### 第一层：化学协议操作（XDL/JSON）

```
Add(reagent, vessel, amount)
HeatChill(vessel, temp, time)
Stir(vessel, speed, time)
Transfer(source, target, volume)
Evaporate(vessel, temp, pressure)
Filter(vessel, filter_type)
```

### 第二层：设备操作（UniLab Actions）

```
transfer_liquid(sources, targets, volumes)
heat_chill(temp, time, stir_speed)
stir(speed, duration)
pump_aspirate(volume, rate)
pump_dispense(volume, rate)
set_valve_position(position)
```

### 第三层：PyLabRobot 原语（仅液体处理）

```
pick_up_tips(tip_spots)
aspirate(wells, volumes, flow_rates)
dispense(wells, volumes, flow_rates)
move_to(coordinate)
discard_tips()
```

### 第四层：硬件指令

```
# 电机控制
move_xyz(x, y, z)
move_z(z)

# 泵控制
pump_set_volume(volume)
pump_set_rate(rate)
pump_run()

# 阀门控制
valve_set_position(port)

# 温控
heater_set_temp(temp)
heater_on()
heater_off()

# 通信协议
Modbus: write_register(address, value)
OPC-UA: write_node(node_id, value)
HTTP: POST /api/command {action, params}
```

---

## 十一、操作编译的依赖关系

### 依赖设备连接图的操作

| 操作 | 依赖的 Graph 信息 |
|------|------------------|
| **transfer_liquid** | slot → deck position 映射, tip rack 位置, 可达性验证 |
| **move_labware** | source/target 位置, 机械臂可达范围 |
| **heat_chill** | vessel 位置, 加热器位置 |
| **pump_aspirate/dispense** | 泵端口 → 容器端口映射 |
| **set_valve_position** | 阀门端口 → 管路连接映射 |

### 不依赖 Graph 的操作

| 操作 | 说明 |
|------|------|
| **stir** | 仅控制搅拌器转速 |
| **get_status** | 查询设备状态 |
| **abort** | 中止当前操作 |
| **initialize** | 设备初始化 |

---

## 十二、操作注册表结构

每个操作在 YAML 中的定义包含：

```yaml
action_name:
  goal:              # 输入参数映射
    param1: param1
    param2: param2
  goal_default:      # 默认值
    param1: 0.0
    param2: ""
  schema:            # JSON Schema 验证
    properties:
      param1:
        type: number
      param2:
        type: string
  handles:           # 数据流连接
    input:
      - handler_key: sources
        data_type: resource
    output:
      - handler_key: targets
        data_type: resource
  placeholder_keys:  # UI 占位符
    param1: unilabos_resources
```

---

## 十三、总结

### 支持的设备类别（31 种）

1. 液体处理器（3种）
2. 温度控制（3种）
3. 机械臂/AGV（4种）
4. 泵阀（4种）
5. 分析仪器（5种）
6. 有机合成（4种）
7. 工作站（4种）
8. 电池测试（1种）
9. 其他（3种）

### 核心编译操作（按使用频率）

| 排名 | 操作 | 使用场景 |
|------|------|---------|
| 1 | **transfer_liquid** | 所有液体转移场景 |
| 2 | **heat_chill** | 温度控制实验 |
| 3 | **incubation** | 生物实验 |
| 4 | **move_labware** | 自动化工作流 |
| 5 | **pump_aspirate/dispense** | 有机合成 |
| 6 | **mix** | 反应混合 |
| 7 | **evaporate** | 溶剂去除 |
| 8 | **filter** | 固液分离 |

### 编译复杂度

| 操作 | 编译层数 | 生成指令数 | 依赖 Graph |
|------|---------|-----------|-----------|
| transfer_liquid | 4 | 10-50 | ✅ |
| heat_chill | 3 | 5-10 | ✅ |
| pump_aspirate | 2 | 3-5 | ✅ |
| stir | 2 | 2-3 | ❌ |
| get_status | 1 | 1 | ❌ |

---

**文档版本**: 1.0
**最后更新**: 2026-03-15
**基于**: UniLab v0.10.18
