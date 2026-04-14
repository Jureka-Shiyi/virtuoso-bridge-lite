# 读取布局几何信息

## 功能概述

本示例展示如何从当前打开的布局 cell 中读取详细的形状几何信息，包括：
- 矩形 (rectangles)
- 路径 (paths)
- 多边形 (polygons)
- 实例 (instances)
- 标签 (labels)

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 06_read_layout.py
```

## 代码逻辑解析

### 读取布局几何

```python
result = client.layout.read_geometry(lib, cell, timeout=30)
```

### 解析输出

```python
output = decode_skill(result.output or "")
if output.startswith("ERROR"):
    print(output)
    return 1

geometry = result.metadata.get("geometry") or parse_layout_geometry_output(result.output or "")
```

### 输出格式化

```python
for obj in geometry:
    _print_object(obj)
```

## 布局读取 API

```python
client.layout.read_geometry(lib, cell, *, timeout=30)
```

返回的 `geometry` 是一个包含所有几何对象的列表，每个对象格式如下：

```json
{
  "type": "rect",
  "layer": "M1",
  "purpose": "drawing",
  "bbox": [x1, y1, x2, y2]
}
```

## 输出示例

```json
{
  "lib": "myLib",
  "cell": "myCell",
  "view": "layout"
}
{
  "type": "rect",
  "layer": "M1",
  "purpose": "drawing",
  "bbox": [0.0, 0.0, 10.0, 5.0]
}
{
  "type": "path",
  "layer": "M2",
  "purpose": "drawing",
  "points": [[0.0, 2.5], [5.0, 2.5]],
  "width": 0.1
}
```

## 几何对象类型

| 类型 | 说明 |
|------|------|
| `rect` | 矩形 |
| `path` | 路径/走线 |
| `polygon` | 多边形 |
| `instance` | 实例 |
| `label` | 标签 |

## 适用场景

- 设计规则检查 (DRC)
- 提取布局 parasitic 参数
- 验证布局完整性
- 自动化测试

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
