# Layout 读取解析工具

## 功能概述

解析 Layout SKILL 操作返回的原始输出，将几何数据转换为 Python 字典。

## 主要函数

### `parse_layout_geometry_output(raw: str) -> list[dict[str, Any]]`

解析 `layout_read_geometry` 返回的逐行几何数据。

**参数**: `raw: str` - SKILL 返回的原始字符串

**返回**: `list[dict]` - 结构化对象列表

**解析的字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `kind` | `str` | 对象类型 ("shape" 或 "instance") |
| `objType` | `str` | shape 类型 (rect, polygon, path 等) |
| `layer` | `str` | 层名 |
| `purpose` | `str` | 目的 |
| `bbox` | `list` | 边界框 `[[x1,y1], [x2,y2]]` |
| `points` | `list` | 点列表 |
| `xy` | `tuple` | 位置坐标 |
| `orient` | `str` | 朝向 |
| `text` | `str` | 标签文本 |
| `name` | `str` | 实例名称 (仅 instance) |
| `lib` | `str` | 库名 (仅 instance) |
| `cell` | `str` | cell 名 (仅 instance) |
| `view` | `str` | 视图名 (仅 instance) |
| `transform` | `str` | 变换矩阵 (仅 instance) |

**使用示例**:

```python
from virtuoso_bridge.virtuoso.layout.reader import parse_layout_geometry_output

raw_output = client.execute_skill(
    'layout_read_geometry("myLib", "myCell" "layout")'
).output

geometry = parse_layout_geometry_output(raw_output)

for obj in geometry:
    if obj["kind"] == "shape":
        print(f"Shape: {obj['objType']} on {obj['layer']}/{obj['purpose']}")
    else:
        print(f"Instance: {obj['name']} at {obj['xy']}")
```

## 内部函数

### `_decode_skill_output(raw: str) -> str`

解码 SKILL 字符串（处理引号和转义）。

### `_parse_skill_numbers(value: str) -> list[float]`

从 SKILL 值中提取数字列表。

### `_parse_skill_point(value: str) -> tuple[float, float] | None`

解析 SKILL 点 `(x y)` 为元组。

### `_parse_skill_point_list(value: str) -> list[tuple[float, float]] | None`

解析 SKILL 点列表为坐标元组列表。
