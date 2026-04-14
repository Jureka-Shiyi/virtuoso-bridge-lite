# 创建演示布局

## 功能概述

本示例展示如何使用 LayoutEditor 上下文管理器创建一个包含基本 shapes 和 TSMC28 实例的演示布局。

## 使用方法

```bash
python 01_create_layout.py <LIB>
```

## 电路结构

创建的布局包含：
- NCH 晶体管实例 (`tsmcN28/nch_ulvt_mac`)
- PCH 晶体管实例 (`tsmcN28/pch_ulvt_mac`)
- MOM 电容实例 (`tsmcN28/cfmom_2t`)
- 金属走线 (M1, M2)
- 标签标注

## 代码逻辑解析

### LayoutEditor 上下文管理器

```python
with client.layout.edit(lib_name, cell_name) as layout:
    layout.add(inst(pdk_lib, "nch_ulvt_mac", "layout", "M0", 0.0, 0.0, "R0"))
    layout.add(inst(pdk_lib, "pch_ulvt_mac", "layout", "M1", 2.0, 0.0, "R0"))
    layout.add(inst(pdk_lib, "cfmom_2t", "layout", "C0", 4.0, 0.0, "R0"))
```

**关键特性**：
- **自动保存**：`dbSave()` 在成功退出时自动调用
- **自动回滚**：异常发生时自动 rollback
- **批量操作**：所有操作在 exit 时统一执行

### 创建的元素

| 元素类型 | 函数 | 参数 |
|---------|------|------|
| 参数化实例 | `layout_create_param_inst` | lib, cell, view, inst_name, x, y, orient |
| 矩形 | `layout_create_rect` | layer, purpose, x1, y1, x2, y2 |
| 路径 | `layout_create_path` | layer, purpose, points, width |
| 标签 | `layout_create_label` | layer, purpose, x, y, text, align, orient, font, height |

### 路径创建示例

```python
layout.add(path("M2", "drawing", [(1.0, 0.25), (3.0, 0.25)], width=0.1))
```

### 标签创建示例

```python
layout.add(label("M1", "pin", 1.1, 0.5, "IN", "centerLeft", "R0", "default", 0.1))
```

## 布局操作 API 速查

| 函数 | 作用 |
|------|------|
| `layout.add()` | 添加布局元素 |
| `layout_create_rect()` | 创建矩形 |
| `layout_create_path()` | 创建路径 |
| `layout_create_label()` | 创建标签 |
| `layout_create_polygon()` | 创建多边形 |
| `layout_create_inst()` | 创建实例 |
| `layout_create_param_inst()` | 创建参数化实例 |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- PDK 库 (`tsmcN28`) 已存在于 Virtuoso 中
