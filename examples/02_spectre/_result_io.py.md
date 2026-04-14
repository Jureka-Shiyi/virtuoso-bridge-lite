# Spectre 仿真结果 IO 辅助函数

## 功能概述

提供 Spectre 仿真结果输出的常用工具函数，包括：
- 保存波形为 CSV
- 保存结果摘要为 JSON
- 打印时序统计
- 打印错误/警告计数

## 核心函数

### `save_waveforms_csv()`

```python
def save_wavesform_csv(data: dict[str, Any], path: Path) -> None:
    """将解析后的波形数组写入 CSV 文件"""
```

将波形数据保存为矩形 CSV 格式，每列一个信号。

### `save_summary_json()`

```python
def save_summary_json(
    result: SimulationResult,
    path: Path,
    extra: dict[str, Any] | None = None,
) -> None:
    """写入不含完整波形数组的紧凑 JSON 摘要"""
```

保存仿真结果的元数据，不重复保存波形数组。

### `print_timing_summary()`

```python
def print_timing_summary(result: SimulationResult) -> None:
    """打印一致的顺序展示运行时序字段"""
```

打印的时序字段包括：
- `upload_total` - 上传总时间
- `remote_exec` - 远程执行时间
- `download_total` - 下载总时间
- `parse_results` - 解析结果时间
- `total` - 总时间

### `print_result_counts()`

```python
def print_result_counts(result: SimulationResult) -> None:
    """打印简洁的错误和警告计数"""
```

## 使用示例

```python
from _result_io import print_result_counts, print_timing_summary, save_summary_json, save_waveforms_csv

# 运行仿真
result = sim.run_simulation(netlist, {})

# 打印状态
print(f"Status: {result.status.value}")
print_result_counts(result)

# 保存波形
save_waveforms_csv(result.data, CSV_PATH)

# 保存摘要
save_summary_json(result, SUMMARY_PATH, extra={"mode": "ax"})

# 打印时序
print_timing_summary(result)
```

## 前置条件

本模块是辅助模块，被其他 Spectre 示例调用，本身不直接运行仿真。
