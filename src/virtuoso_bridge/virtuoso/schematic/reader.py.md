# Schematic 读取工具

## 功能概述

统一读取 schematic 数据，支持拓扑、位置、注释和 CDF 参数。

## 主要 API

### `read_schematic(client, lib=None, cell=None, *, include_positions=False, param_filters=_DEFAULT_FILTERS_PATH) -> dict`

一次性读取 schematic。

**参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lib` | `str \| None` | `None` | 库名（省略则使用当前 cellview） |
| `cell` | `str \| None` | `None` | Cell 名（省略则使用当前 cellview） |
| `include_positions` | `bool` | `False` | 是否包含 xy/orient/bBox/numInst/view |
| `param_filters` | `str \| Path \| None` | `cdf_param_filters.yaml` | 参数过滤器配置路径 |

**返回**: `dict`，包含 keys: `instances`, `nets`, `pins`, `notes`

```python
from virtuoso_bridge.virtuoso.schematic.reader import read_schematic

# 完整读取（拓扑 + 位置 + 注释）
data = read_schematic(client, "myLib", "myCell", include_positions=True)

# 拓扑只读（无 xy/orient/bBox）
data = read_schematic(client, "myLib", "myCell", include_positions=False)

# 无参数过滤（返回所有 CDF 参数）
data = read_schematic(client, "myLib", "myCell", param_filters=None)
```

### 返回数据结构

```python
{
    "instances": [
        {
            "name": "M0",
            "lib": "tsmcN28",
            "cell": "nch",
            "terms": {"D": "OUT", "G": "IN", "S": "VSS"},
            "params": {"w": "1u", "l": "30n"},
            # include_positions=True 时还有:
            "xy": [0.0, 0.0],
            "orient": "R0",
            "bBox": [[-0.5, -0.5], [0.5, 0.5]],
            "numInst": 1,
            "view": "symbol"
        },
        ...
    ],
    "nets": {
        "VDD": {
            "connections": ["M0.D", "M1.S"],
            "numBits": 1,
            "sigType": "signal",
            "isGlobal": True
        },
        ...
    },
    "pins": {
        "IN": {"direction": "input", "numBits": 1},
        "OUT": {"direction": "output", "numBits": 1}
    },
    "notes": [
        {"text": "bias", "xy": [1.0, 2.0], "font": "stick", "height": 0.1, ...}
    ]
}
```

## 旧版 API（向后兼容）

### `read_placement(client, lib=None, cell=None) -> dict`

读取布局：实例位置、引脚、标签、导线。

### `read_connectivity(client, lib=None, cell=None) -> dict`

读取电气连接：实例、网、引脚。

### `read_instance_params(client, lib=None, cell=None, filter_params=None) -> list[dict]`

读取所有实例的 CDF 参数。

## 参数过滤

`cdf_param_filters.yaml` 文件示例：

```yaml
filters:
  - match:
      lib: "tsmcN28"
      cell: "nch*"
    params: ["w", "l", "nf", "m"]

fallback: all  # 或指定列表
```

## 内部解析函数

### `_parse_schematic(raw, include_positions, filter_config) -> dict`

解析原始 SKILL 输出为结构化字典。

### `_parse_point(s: str) -> list[float]`

解析 SKILL 点 `(1.5 -2.0)` → `[1.5, -2.0]`

### `_parse_bbox(s: str) -> list[list[float]]`

解析 SKILL bBox `((x1 y1) (x2 y2))` → `[[x1,y1],[x2,y2]]`
