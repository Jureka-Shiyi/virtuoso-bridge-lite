# Schematic 模块

## 功能概述

Cadence Virtuoso Schematic 编辑的 SKILL 构建器和编辑器封装。

## 导出内容

### 类

| 类 | 说明 |
|---|---|
| `SchematicEditor` | Schematic 批量编辑的上下文管理器 |
| `SchematicOps` | 挂载在 VirtuosoClient 上的 `client.schematic` |

### 实例创建

| 函数 | 说明 |
|------|------|
| `schematic_create_inst` | 创建实例 |
| `schematic_create_inst_by_master_name` | 通过 master 名称创建实例 |

### 导线创建

| 函数 | 说明 |
|------|------|
| `schematic_create_wire` | 创建导线 |
| `schematic_create_wire_label` | 创建导线标签 |
| `schematic_create_wire_between_instance_terms` | 连接两端子 |

### 端子标签

| 函数 | 说明 |
|------|------|
| `schematic_label_instance_term` | 为实例端子添加网络标签 |

### 引脚创建

| 函数 | 说明 |
|------|------|
| `schematic_create_pin` | 创建引脚 |
| `schematic_create_pin_at_instance_term` | 在端子处创建引脚 |

### 检查

| 函数 | 说明 |
|------|------|
| `schematic_check` | 运行 schematic 检查 |

## 使用示例

```python
from virtuoso_bridge import VirtuosoClient

client = VirtuosoClient.from_env()

# 通过 client.schematic 访问 SchematicOps
with client.schematic.edit("myLib", "inv") as sch:
    sch.add(schematic_create_inst_by_master_name(
        "tsmcN28", "nch_ulvt_mac", "symbol", "M0", 0, 0, "R0"
    ))
    sch.add_net_label_to_transistor(
        "M0", drain_net="OUT", gate_net="IN", source_net="VSS"
    )
# 自动检查和保存
```
