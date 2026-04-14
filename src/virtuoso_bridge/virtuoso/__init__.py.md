# Virtuoso 工具家族

## 功能概述

Cadence Virtuoso 控制和编辑原语的工具家族封装。

## 子包

| 子包 | 说明 |
|------|------|
| `virtuoso.basic` | VirtuosoClient（通过 TCP 执行 SKILL） |
| `virtuoso.schematic` | Schematic 编辑的 SKILL 构建器 |
| `virtuoso.layout` | Layout 编辑的 SKILL 构建器 |

## 导入

```python
from virtuoso_bridge.virtuoso.basic.bridge import VirtuosoClient
```

## 主要组件

### VirtuosoClient

通过 RAMIC 守护进程在 Virtuoso 中执行 SKILL 代码的 Python 客户端。

```python
from virtuoso_bridge import VirtuosoClient

client = VirtuosoClient.from_env()
result = client.execute_skill("1+2")
print(result.output)
```

### Schematic 编辑

```python
from virtuoso_bridge.virtuoso.schematic import SchematicEditor

with client.schematic.edit("myLib", "inv") as sch:
    sch.add(schematic_create_inst(...))
    sch.add(schematic_label_instance_term(...))
```

### Layout 编辑

```python
from virtuoso_bridge.virtuoso.layout import LayoutEditor

with client.layout.edit("myLib", "layout") as lay:
    lay.add(layout_create_rect("M1", "drawing", 0, 0, 1, 0.5))
    lay.add(layout_create_via_by_name("M1_M2", 0.5, 0.25))
```
