# Schematic CDF 参数设置

## 功能概述

在 schematic 实例上设置 CDF 参数，并触发回调刷新。

## 主要函数

### `set_instance_params(client, inst_name, *, w=None, wf=None, l=None, nf=None, m=None) -> None`

在特定实例上设置器件参数，然后触发 CDF 回调。

**参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `w` | `str \| None` | `None` | 总宽度（如 "2u"）。w = wf × nf |
| `wf` | `str \| None` | `None` | 指宽（如 "500n"）。映射到 CDF 参数 "Wfg" |
| `l` | `str \| None` | `None` | 沟道长度（如 "30n"） |
| `nf` | `str \| None` | `None` | 指数量（如 "4"）。映射到 CDF 参数 "fingers" |
| `m` | `str \| None` | `None` | 倍数器（如 "2"） |

**使用示例**:

```python
from virtuoso_bridge.virtuoso.schematic.params import set_instance_params

# 设置总宽度和沟道长度
set_instance_params(client, "MP0", w="2u", l="30n")

# 使用指宽（finger width）
set_instance_params(client, "MN0", wf="250n", l="30n", nf="8")

# nf 在某些 PDK（如 TSMC）中是只读的，必须使用 "fingers"
# wf 映射到 "Wfg"（指宽）；w 是总宽度 = Wfg × fingers
```

**异常**:
- `ValueError` - 同时指定 w 和 wf
- `RuntimeError` - schHiReplace 执行失败

**注意**:
- 必须触发 CDF callbacks 以确保参数正确传播到仿真
- 使用 `schHiReplace` 直接设置属性值
- 然后运行 callbacks 更新实例参数
