# 多层金属布线

## 功能概述

本示例演示如何在同一坐标位置添加跨越 M2 到 M7 多层的金属走线。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 04_multilayer_routing.py
```

## 代码逻辑解析

### 多层布线

```python
LAYERS = ["M2", "M3", "M4", "M5", "M6", "M7"]

def add_routing() -> None:
    with client.layout.edit(lib, cell, mode="a") as layout:
        for layer in LAYERS:
            layout.add(path(
                layer,
                "drawing",
                [(X_START, Y), (X_END, Y)],
                width=PATH_WIDTH
            ))
```

在相同的起点和终点坐标上，为每一层金属创建一条路径。

### 路径参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `X_START` | 0.0 | 路径起点 X |
| `X_END` | 5.0 | 路径终点 X |
| `Y` | 3.0 | 路径 Y 坐标 |
| `PATH_WIDTH` | 0.1 | 金属宽度 (um) |

## 走线创建函数

```python
layout_create_path(layer, purpose, points, width)
```

| 参数 | 说明 |
|------|------|
| `layer` | 金属层名称 |
| `purpose` | 目的（如 "drawing"） |
| `points` | 路径点坐标列表 `[(x1,y1), (x2,y2)]` |
| `width` | 路径宽度 |

## 金属层速查

| 层名 | 说明 |
|------|------|
| M1 | 最低层金属 |
| M2 | 第二层金属 |
| M3-M7 | 中间层金属 |
| AP | 顶层金属 |

## 适用场景

- 创建测试结构
- 金属层兼容性验证
- 定制化布局设计

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载
