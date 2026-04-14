# 删除指定层上的所有形状

## 功能概述

本示例演示如何从当前布局中删除指定层和目的的所有形状（shapes），同时保留实例 (instances)。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 07_delete_shapes_on_layer.py
```

## 代码逻辑解析

### 配置要删除的层

```python
DELETE_LAYER = "M3"
DELETE_PURPOSE = "drawing"
```

### 列出当前 shapes

```python
result = client.layout.list_shapes(timeout=15)
shapes = decode_skill(result.output or "")
print("Shapes in open layout:")
print(shapes or "  (none)")
```

### 删除指定层上的 shapes

```python
result = client.layout.delete_shapes_on_layer(
    DELETE_LAYER,
    DELETE_PURPOSE,
    timeout=30
)
```

### 删除后保存

```python
client.save_current_cellview(timeout=15)
```

## 删除操作 API

| 函数 | 作用 |
|------|------|
| `layout.list_shapes()` | 列出当前布局中的所有 shapes |
| `layout.delete_shapes_on_layer()` | 删除指定层/目的的所有 shapes |
| `layout.clear_routing()` | 清除所有 routing shapes |
| `layout.clear_current()` | 清除当前所有可见图元 |

## 层和目的 (Layer/Purpose)

Virtuoso 中的每个几何对象都有：
- **Layer**：物理层（如 M1, M2, M3）
- **Purpose**：目的类型

| 常见 Purpose | 说明 |
|-------------|------|
| `drawing` | 绘图层 |
| `pin` | 引脚层 |
| `label` | 标签层 |
| `net` | 网络层 |

## 适用场景

- 清理手动绘制的临时图形
- 批量修改布局
- 准备重新布线

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
