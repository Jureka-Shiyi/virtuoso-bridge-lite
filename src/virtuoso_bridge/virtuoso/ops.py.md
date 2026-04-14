# SKILL 操作构建器

## 功能概述

共享的 SKILL 操作构建函数，为 virtuoso 工具家族生成 SKILL 代码字符串。

## 主要函数

### 字符串处理

#### `escape_skill_string(value: str) -> str`

转义 Python 字符串用于 SKILL 字符串字面量。

```python
escape_skill_string('hello "world"')
# 返回: 'hello \\"world\\"'
```

### 视图类型

#### `default_view_type_for(view: str) -> str`

将逻辑视图名映射到期望的 viewType。

```python
default_view_type_for("layout")   # -> "maskLayout"
default_view_type_for("schematic") # -> "schematic"
default_view_type_for("symbol")   # -> "symbol"
```

### 点和坐标

#### `skill_point(x: float, y: float) -> str`

渲染 SKILL 点字面量。

```python
skill_point(1.5, 2.3)
# 返回: "'(1.500 2.300)"
```

#### `skill_point_list(points: Iterable[tuple[float, float]]) -> str`

渲染 SKILL 点列表字面量。

```python
skill_point_list([(0, 0), (1.5, 2.3), (3.0, 4.5)])
# 返回: "'((0.000 0.000) (1.500 2.300) (3.000 4.500))"
```

### CellView 操作

#### `open_cell_view(lib, cell, *, view="layout", view_type=None, mode="w") -> str`

构建打开并绑定目标 cellview 到 `cv` 的 SKILL。

```python
open_cell_view("myLib", "myCell", view="layout", mode="w")
# 返回 SKILL 代码: cv = dbOpenCellViewByType("myLib" "myCell" "layout" "maskLayout" "w")
```

#### `open_window(lib, cell, *, view="layout", view_type=None, mode="a") -> str`

构建打开 Virtuoso 窗口的 SKILL。

如果已存在相同 lib/cell/view 的窗口，则聚焦该窗口而非打开新窗口。

```python
open_window("myLib", "myCell", view="layout")
```

#### `save_current_cellview() -> str`

构建保存当前编辑 cellview 或绑定 `cv` 的 SKILL。

```python
save_current_cellview()
```

#### `close_current_cellview() -> str`

构建关闭当前编辑 cellview 或绑定 `cv` 的 SKILL。

```python
close_current_cellview()
```

#### `clear_current_layout() -> str`

构建删除当前布局编辑器中所有可见图形的 SKILL。

```python
clear_current_layout()
# 删除所有 shapes 并 redraw
```
