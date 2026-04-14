# Schematic 编辑器

## 功能概述

批量 SKILL 操作的上下文管理器，用于在 Virtuoso Schematic 编辑器中批量执行操作。

## SchematicEditor 类

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `client` | `VirtuosoClient` | - | Virtuoso 客户端 |
| `lib` | `str` | - | 库名 |
| `cell` | `str` | - | Cell 名 |
| `view` | `str` | `"schematic"` | 视图名 |
| `mode` | `str` | `"w"` | 打开模式 |
| `timeout` | `int` | `60` | 超时时间（秒） |

### 核心方法

| 方法 | 说明 |
|------|------|
| `add(skill_cmd)` | 添加 SKILL 命令到批处理 |
| `add_net_label_to_transistor(instance_name, drain_net, gate_net, source_net, body_net)` | 为 MOS 端点 D/G/S/B 添加网络标签 |

### 使用示例

```python
from virtuoso_bridge.virtuoso.schematic.editor import SchematicEditor
from virtuoso_bridge.virtuoso.schematic.ops import (
    schematic_create_inst_by_master_name,
    schematic_create_pin,
)

with client.schematic.edit("myLib", "inv") as sch:
    # 添加实例
    sch.add(schematic_create_inst_by_master_name(
        "tsmcN28", "nch_ulvt_mac", "symbol", "M0", 0, 0, "R0"
    ))
    # 为晶体管端子添加网络标签
    sch.add_net_label_to_transistor(
        "M0", drain_net="OUT", gate_net="IN", source_net="VSS", body_net="VSS"
    )
    # 添加引脚
    sch.add(schematic_create_pin("IN", -1.0, 0.75, "R0", direction="input"))
    sch.add(schematic_create_pin("OUT", 1.0, 0.75, "R0", direction="output"))
# 自动执行: schCheck + dbSave on exit
```

## 错误处理

- SKILL 执行失败时抛出 `RuntimeError`
- 异常时跳过检查和保存
