# 添加过孔 (Via)

## 功能概述

本示例展示两种添加过孔的方法：
1. **按名称添加** (`via_by_name`) - 使用标准过孔名称
2. **原始 API** (`via`) - 直接使用 viaDef 表达式

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 03_add_via.py
```

## 代码逻辑解析

### 方法一：按名称添加过孔

```python
layout.add(via_by_name(
    VIA_NAME,      # "M2_M1"
    BY_NAME_VIA_X,
    BY_NAME_VIA_Y,
    orientation="R0",
))
```

**优点**：代码更易读，使用标准过孔名称。

### 方法二：使用 ViaDef 表达式

```python
layout.add(via(
    via_def_from_name(VIA_NAME),  # 获取 ViaDef 表达式
    RAW_VIA_X,
    RAW_VIA_Y,
    VIA_ORIENTATION,
    "nil",
))
```

**优点**：更灵活，可自定义参数。

### ViaDef 表达式

```python
via_def_from_name(VIA_NAME)
# 返回类似: "ViaDef(\"M2_M1\" ...)" 的 SKILL 表达式
```

## 关键函数

| 函数 | 作用 |
|------|------|
| `layout_create_via_by_name` | 按名称创建过孔 |
| `layout_create_via` | 使用 ViaDef 创建过孔 |
| `layout_via_def_expr_from_name` | 获取 ViaDef 表达式 |

## 过孔参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `VIA_NAME` | 过孔名称 | `"M2_M1"` |
| `X, Y` | 放置坐标 | `1.5, 0.25` |
| `orientation` | 旋转方向 | `"R0"`, `"R90"`, `"R180"`, `"R270"` |

## 常见过孔类型

| 过孔名称 | 说明 |
|---------|------|
| `M1_M2` | Metal1 到 Metal2 |
| `M2_M3` | Metal2 到 Metal3 |
| `M3_M4` | Metal3 到 Metal4 |
| `VIA` | 标准通孔 |

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
- PDK 过孔定义已加载
