# Schematic SKILL 操作构建器

## 功能概述

Schematic 编辑的 SKILL 操作构建函数，生成创建实例、导线、引脚等的 SKILL 代码。

## 主要函数

### 实例创建

#### `schematic_create_inst(master_expr, instance_name, x, y, orientation, *, cv_expr="cv") -> str`

创建 schematic 实例。

#### `schematic_create_inst_by_master_name(lib, cell, view, instance_name, x, y, orientation, *, cv_expr="cv", view_type=None, mode="r") -> str`

通过 master 名称打开 cellview 并创建实例。

```python
schematic_create_inst_by_master_name(
    "tsmcN28", "nch_ulvt_mac", "symbol", "M0", 0, 0, "R0"
)
```

### 导线创建

#### `schematic_create_wire(points, *, cv_expr="cv", route_style="route", route_mode="full") -> str`

从一系列点创建导线。

```python
schematic_create_wire([(0, 0), (1.5, 0), (1.5, 1.0)])
```

#### `schematic_create_wire_label(x, y, text, justification, rotation, *, cv_expr="cv", style="stick", height=0.0625) -> str`

创建导线标签。

```python
schematic_create_wire_label(0.75, 0, "VDD", "centerCenter", "R0")
```

#### `schematic_create_wire_between_instance_terms(from_instance, from_term, to_instance, to_term, *, cv_expr="cv", route_style="route", route_mode="full") -> str`

直接连接两个实例端子的导线。

```python
schematic_create_wire_between_instance_terms("M0", "D", "M1", "S")
```

### 端子标签

#### `schematic_label_instance_term(instance_name, term_name, net_name, *, cv_expr="cv", justification="centerCenter", rotation="R0", style="stick", height=0.0625, extension_length=0.25) -> str`

在实例端子处放置带标签的导线桩。

用于 MOS 端点 D/G/S/B 自动化标注：

```python
# 手动逐端点标注
schematic_label_instance_term("M0", "D", "OUT")
schematic_label_instance_term("M0", "G", "IN")
schematic_label_instance_term("M0", "S", "VSS")
schematic_label_instance_term("M0", "B", "VSS")
```

### 引脚创建

#### `schematic_create_pin(pin_name, x, y, orientation, *, cv_expr="cv", direction="inputOutput") -> str`

创建引脚。

- `direction`: "input", "output", "inputOutput"

```python
schematic_create_pin("DATA", 0, 0, "R0", direction="inputOutput")
```

#### `schematic_create_pin_at_instance_term(instance_name, term_name, pin_name, *, cv_expr="cv", direction="inputOutput", orientation="R0") -> str`

在实例端子中心创建引脚。

```python
schematic_create_pin_at_instance_term("M0", "D", "OUT", direction="output")
```

### 检查

#### `schematic_check(*, cv_expr="cv") -> str`

构建运行 schematic 检查的 SKILL。

```python
schematic_check()
```
