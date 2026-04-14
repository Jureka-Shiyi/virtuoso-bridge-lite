# 从现有设计重新创建原理图

读取现有原理图，映射到网格，用 stub 重新绘制。适用于从参考设计中学习布局或生成变体。

## 步骤 1：读取原始设计

提取实例、连接和位置：

```python
from virtuoso_bridge.virtuoso.schematic.reader import read_schematic

data = read_schematic(client, LIB, CELL, include_positions=True)
# data["instances"] 有每个实例的 xy、orient、params、terms
```

## 步骤 2：映射到网格

分析相对位置，在统一网格上分配（列，行）：

- 按 y 排序实例 -> 分配行（垂直层）
- 每行内按 x 排序 -> 分配列
- 识别差分对（同一行，对称 x）-> 左边 R0，右边 MY
- 选择 GRID 间距（1.5 效果很好，stub 标签不会碰撞）

## 步骤 3：重绘

在网格上放置，带 stub 和引脚：

```python
GRID = 1.5

# 定义放置为 (name, cell, col, row, orient)
INSTANCES = [
    ("M_TAIL", "nch_ulvt_mac", 1.5, 0, "R0"),   # 居中
    ("M_INP",  "nch_ulvt_mac", 1,   1, "R0"),    # 对左边
    ("M_INN",  "nch_ulvt_mac", 2,   1, "MY"),    # 右边，镜像
    ...
]

# 定义连接为 (name, drain, gate, source, body)
LABELS = [
    ("M_TAIL", "VS",  "CLK",  "GND", "GND"),
    ("M_INP",  "VN1", "VINP", "VS",  "GND"),
    ...
]

with client.schematic.edit(LIB, CELL) as sch:
    for name, cell, col, row, orient in INSTANCES:
        sch.add(inst(PDK, cell, "symbol", name, col * GRID, row * GRID, orient))
    for name, d, g, s, b in LABELS:
        sch.add_net_label_to_transistor(name,
            drain_net=d, gate_net=g, source_net=s, body_net=b)
    # 引脚在最左边列
    sch.add(pin("VINP", -1 * GRID, 1 * GRID, "R0", direction="input"))
    ...
```

## 关键规则

- **网格间距 1.5**——足够的空间放置 stub 而不碰撞。太小的间距（< 1.0）会导致重叠，太大（> 2.0）会浪费空间。
- **差分对：R0/MY**——左边器件 `R0`，右边器件 `MY`，同一行，对称列。
- **垂直分层**——NMOS 在底部（低行），PMOS 在顶部（高行）。在一级内：电流源 -> 信号路径 -> 负载。
- **引脚在专用列**——总是在所有晶体管的左边（例如 col = -1）。
- **输出级右移**——放在 col 5-6，与核心分开。
- **不布线**——只用 `add_net_label_to_transistor`。相同 net 名称 = 相同 net。
- **用 CIW 截图验证**——每次运行后检查 PARSER WARNING 或 schCheck 错误。
