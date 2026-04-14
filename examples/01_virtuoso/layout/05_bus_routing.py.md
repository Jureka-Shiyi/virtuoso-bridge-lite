# 添加 8 位总线标记路由

## 功能概述

本示例演示如何创建带有标签的 8 位总线（bus）走线，每位有独立的标签如 `CODE<0>`, `CODE<1>`, ..., `CODE<7>`。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 05_bus_routing.py
```

## 代码逻辑解析

### 总线参数配置

```python
BUS_WIDTH = 8                    # 8 位总线
PATH_WIDTH = 0.05                # 线宽 (um)
BUS_PITCH = 0.1                  # 相邻位间距 (um)
X_START = 0.0                    # 总线起点 X
X_END = 5.0                      # 总线终点 X
Y_BASE = 2.0                     # 第一位 (CODE<0>) 的 Y 坐标
```

### 循环创建每位走线

```python
for bit in range(BUS_WIDTH):
    y = Y_BASE + bit * BUS_PITCH

    # 在每层金属上创建路径
    for layer in LAYERS:
        layout.add(path(layer, "drawing", [(X_START, y), (X_END, y)], width=PATH_WIDTH))

    # 添加标签
    layout.add(label(
        LABEL_LAYER, "pin",
        X_START, y,
        f"CODE<{bit}>",  # CODE<0>, CODE<1>, ... CODE<7>
        "centerLeft", "R0", "default",
        LABEL_HEIGHT,
    ))
```

### 总线布局示意

```
CODE<7> ────────────────────────────────────  (M4, y=2.7)
CODE<6> ────────────────────────────────────  (M4, y=2.6)
CODE<5> ────────────────────────────────────  (M4, y=2.5)
CODE<4> ────────────────────────────────────  (M4, y=2.4)
CODE<3> ────────────────────────────────────  (M4, y=2.3)
CODE<2> ────────────────────────────────────  (M4, y=2.2)
CODE<1> ────────────────────────────────────  (M4, y=2.1)
CODE<0> ────────────────────────────────────  (M4, y=2.0)
        X=0.0                              X=5.0
```

## 标签创建函数

```python
layout_create_label(
    layer,           # "M4"
    purpose,         # "pin"
    x, y,           # 位置坐标
    text,           # "CODE<0>", "CODE<1>", ...
    align,          # "centerLeft", "centerRight", "centerCenter"
    orient,         # "R0"
    font,           # "default"
    height          # 标签高度
)
```

## 输出结果

```
[Done] 8-bit bus routing CODE<7:0> added
```

## 适用场景

- 数字模块的总线连接
- 多位信号线的统一标注
- 自动生成测试结构

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
