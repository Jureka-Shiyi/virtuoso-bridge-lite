# Maestro 配置和结果读取

## 功能概述

读取 Maestro 配置、环境设置和仿真结果。

## 主要函数

### `read_config(client, session) -> dict[str, tuple[str, str]]`

读取测试配置：测试、分析、输出、变量、参数、角落。

**返回**: `dict`，键为 (skill_expr, raw_output) 元组

```python
from virtuoso_bridge.virtuoso.maestro.reader import read_config

config = read_config(client, session)
# 包含:
# - maeGetSetup: 所有测试
# - maeGetEnabledAnalysis: 启用的分析列表
# - maeGetAnalysis:<name>: 每个分析的参数
# - maeGetTestOutputs: 输出列表
# - variables, parameters, corners
```

### `read_env(client, session) -> dict[str, tuple[str, str]]`

读取系统设置：环境选项、仿真选项、运行模式、作业控制。

```python
env = read_env(client, session)
# 包含:
# - maeGetEnvOption: 环境选项
# - maeGetSimOption: 仿真选项
# - maeGetCurrentRunMode: 当前运行模式
# - maeGetJobControlMode: 作业控制模式
# - maeGetSimulationMessages: 仿真消息
```

### `read_results(client, session, lib="", cell="", history="") -> dict[str, tuple[str, str]]`

读取仿真结果：输出值、spec 状态、良率。

**参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `session` | `str` | - | 活动会话字符串 |
| `lib` | `str` | `""` | 库名（自动检测） |
| `cell` | `str` | `""` | Cell 名（自动检测） |
| `history` | `str` | `""` | 显式历史名（如 "Interactive.7"）|

**返回**: `dict`，包含 maeGetResultTests, maeGetOutputValues, maeGetOverallSpecStatus, maeGetOverallYield

```python
results = read_results(client, session)
# 自动扫描最新的 Interactive.N
# 返回仿真输出值和 spec 状态
```

### `export_waveform(client, session, expression, local_path, *, analysis="ac", history="") -> str`

通过 OCEAN 导出波形到本地文本文件。

**参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `session` | `str` | - | 会话字符串 |
| `expression` | `str` | - | OCEAN 表达式，如 `'dB20(mag(VF("/VOUT")))'` |
| `local_path` | `str` | - | 本地保存路径 |
| `analysis` | `str` | `"ac"` | 分析类型 |
| `history` | `str` | `""` | 显式历史名（自动检测） |

**返回**: 本地文件路径

```python
from virtuoso_bridge.virtuoso.maestro.reader import export_waveform

# 导出 AC 波形
export_waveform(
    client, session,
    "dB20(mag(VF(\"/VOUT\")))",
    "./vout_ac.txt",
    analysis="ac"
)

# 导出瞬态波形
export_waveform(
    client, session,
    "VT(\"/OUT\")",
    "./vout_tran.txt",
    analysis="tran"
)
```

## 波形格式

导出的波形文件为单列数值，可直接用 `numpy.loadtxt()` 读取。

## 内部辅助函数

### `_q(client, label, expr) -> tuple[str, str]`

执行 SKILL 并打印到 CIW，返回 (expr, raw_output)。

### `_get_test(client, session) -> str`

获取会话中的第一个测试名。

### `_unique_remote_wave_path(history) -> str`

创建唯一远程路径避免跨用户文件冲突。

### `_history_token(history) -> str`

返回文件系统安全的 token。
