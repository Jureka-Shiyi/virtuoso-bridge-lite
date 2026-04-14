# 在当前布局中添加多边形

## 功能概述

本示例演示如何向当前打开的布局视图添加一个多边形图元。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 02_add_polygon.py
```

## 代码逻辑解析

### 获取当前设计

```python
lib, cell, _ = client.get_current_design()
if not lib:
    print("Open a layout in Virtuoso first.")
    return 1
```

### 追加模式编辑

```python
with client.layout.edit(lib, cell, mode="a") as layout:
    layout.add(polygon(LAYER, PURPOSE, POINTS))
```

`mode="a"` 表示**追加模式**，保留现有内容，仅添加新元素。

### 多边形定义

```python
POINTS = [
    (0.5, 1.8),
    (2.0, 1.8),
    (2.5, 2.2),
    (1.2, 3.0),
    (0.5, 2.4),
]
```

多边形由一组坐标点定义，形成闭合区域。

## 多边形创建函数

```python
from virtuoso_bridge.virtuoso.layout.ops import layout_create_polygon as polygon

polygon(layer, purpose, points)
```

| 参数 | 说明 |
|------|------|
| `layer` | 层名，如 "M3" |
| `purpose` | 目的，如 "drawing"、"pin" |
| `points` | `(x, y)` 坐标列表 |

## 编辑模式

| 模式 | 说明 |
|------|------|
| `"w"` | 写模式，创建新布局或覆盖 |
| `"a"` | 追加模式，保留现有内容 |

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
