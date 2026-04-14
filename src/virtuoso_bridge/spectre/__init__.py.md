# Spectre 仿真模块

## 功能概述

Cadence Spectre 独立仿真的工具家族封装。

## 导入

```python
from virtuoso_bridge.spectre import SpectreSimulator
```

## 导出内容

### 类

| 类 | 说明 |
|---|---|
| `SpectreSimulator` | Spectre 仿真运行器，支持本地和远程仿真 |

## 子模块

| 模块 | 说明 |
|------|------|
| `spectre.runner` | SpectreSimulator 仿真运行器 |
| `spectre.parsers` | PSF ASCII 格式解析器 |

## 使用示例

```python
from virtuoso_bridge.spectre import SpectreSimulator

# 创建仿真器
sim = SpectreSimulator.from_env(
    spectre_args=["-env", "spectre"],
    work_dir="./output"
)

# 运行仿真
result = sim.run_simulation("netlist.scs", {"include_files": ["model.scs"]})

if result.ok:
    # 解析波形数据
    vout = result.data["VOUT"]
```
