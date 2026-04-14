# Schematic Python API

通过 SKILL 控制 Cadence Virtuoso 原理图编辑的 Python 封装。

**包：** `virtuoso_bridge.virtuoso.schematic`

```python
from virtuoso_bridge import VirtuosoClient
client = VirtuosoClient.from_env()
# SchematicOps 通过 client.schematic 访问
```

## SchematicEditor（上下文管理器）

收集 SKILL 命令，在 `__exit__` 时批量执行，然后自动运行 `schCheck` + `dbSave`。

```python
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
    schematic_create_wire_between_instance_terms as wire,
)

with client.schematic.edit(lib, cell) as sch:
    sch.add(inst("analogLib", "vdc", "symbol", "V0", 0, 0, "R0"))
    sch.add(wire("V0", "PLUS", "R0", "PLUS"))
    sch.add(pin("OUT", 3.0, 0.5, "R0", direction="output"))
    sch.add_net_label_to_transistor("M0", drain_net="OUT", gate_net="IN",
        source_net="VSS", body_net="VSS")
    # schCheck + dbSave 在退出时自动执行
```

### SchematicEditor 方法

| 方法 | 描述 |
|------|------|
| `add(skill_cmd)` | 排队任何 SKILL 命令字符串（来自 ops 函数） |
| `add_net_label_to_transistor(inst, drain_net, gate_net, source_net, body_net)` | 用 net stub 标记 MOS D/G/S/B 端子 |

### SKILL 构建函数（ops）

与 `sch.add(...)` 一起使用：

| 函数 | SKILL | 描述 |
|------|-------|------|
| `schematic_create_inst_by_master_name(lib, cell, view, name, x, y, orient)` | `dbOpenCellViewByType` + `dbCreateInst` | 放置实例 |
| `schematic_create_wire(points)` | `schCreateWire` | 从点列表添加导线 |
| `schematic_create_wire_label(x, y, text, just, rot)` | `schCreateWireLabel` | 添加导线标签 |
| `schematic_create_pin(name, x, y, orient, *, direction)` | `schCreatePin` | 添加引脚 |
| `schematic_create_pin_at_instance_term(inst, term, pin, *, direction, orientation)` | 在端子中心 `schCreatePin` | 在端子处添加引脚 |
| `schematic_create_wire_between_instance_terms(from_inst, from_term, to_inst, to_term)` | 在端子中心之间 `schCreateWire` | 为两个端子连线 |
| `schematic_label_instance_term(inst, term, net)` | 导线 stub + 标签 | 标记端子 |

## SchematicOps（直接执行）

与 `SchematicEditor` 相同的操作，但立即执行（不是批量）。

```python
client.schematic.add_instance("analogLib", "vdc", (0, 0), name="V0")
client.schematic.add_wire_between_instance_terms("V0", "PLUS", "R0", "PLUS")
```

| 方法 | SKILL | 描述 |
|------|-------|------|
| `open(lib, cell, *, view, mode)` | `dbOpenCellViewByType` | 打开 cellview |
| `save()` | `dbSave(cv)` | 保存当前 cellview |
| `check()` | `schCheck(cv)` | 运行原理图检查 |
| `add_instance(lib, cell, xy, *, orientation, view, name)` | `dbCreateInst` | 添加实例 |
| `add_wire(points)` | `schCreateWire` | 添加导线 |
| `add_label(xy, text, *, justification, rotation)` | `schCreateWireLabel` | 添加标签 |
| `add_pin(name, xy, *, orientation, direction)` | `schCreatePin` | 添加引脚 |
| `add_pin_to_instance_term(inst, term, pin_name, *, direction, orientation)` | 在端子处 `schCreatePin` | 在端子处添加引脚 |
| `add_wire_between_instance_terms(from_inst, from_term, to_inst, to_term)` | 在端子间 `schCreateWire` | 为两个端子连线 |
| `add_net_label_to_instance_term(inst, term, net_name)` | 导线 stub + 标签 | 标记端子 |
| `add_net_label_to_transistor(inst, drain, gate, source, body)` | 多个导线 stub | 标记 MOS D/G/S/B |

## 低层 SKILL 构建器

`schematic/ops.py`——构建 SKILL 字符串但不执行。由 `SchematicOps` 和 `SchematicEditor` 内部使用。

| 函数 | 生成的 SKILL |
|------|----------------|
| `schematic_create_inst(master_expr, name, x, y, orient)` | `dbCreateInst(cv master ...)` |
| `schematic_create_inst_by_master_name(lib, cell, view, name, x, y, orient)` | `dbOpenCellViewByType` + `dbCreateInst` |
| `schematic_create_wire(points)` | `schCreateWire(cv "route" "full" ...)` |
| `schematic_create_wire_label(x, y, text, just, rot)` | `schCreateWireLabel(cv ...)` |
| `schematic_create_pin(name, x, y, orient)` | `schCreatePin(cv ...)` |
| `schematic_create_pin_at_instance_term(inst, term, pin)` | 端子中心查找 + `schCreatePin` |
| `schematic_create_wire_between_instance_terms(from_inst, from_term, to_inst, to_term)` | 端子中心查找 + `schCreateWire` |
| `schematic_label_instance_term(inst, term, net)` | 端子中心 + MOS 感知 stub + `schCreateWireLabel` |
| `schematic_check()` | `schCheck(cv)` |

## 端子感知辅助函数

`add_wire_between_instance_terms` 和 `add_net_label_to_instance_term` 从数据库解析引脚位置——无需猜测坐标。

`add_net_label_to_transistor` 是 MOS 感知的：它知道 drain/source 上下（PMOS 翻转），gate 在左边，body 在右边。stub 方向适应晶体管方向。
