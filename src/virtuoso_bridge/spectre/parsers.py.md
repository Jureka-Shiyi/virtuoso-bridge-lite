# PSF 解析器

## 功能概述

解析 Spectre PSF ASCII 格式的仿真输出文件，将波形数据转换为 Python 字典。

## 主要函数

### `parse_spectre_psf_ascii(psf_path)`

解析单个 PSF ASCII 文件。

**参数**: `psf_path: Path` - PSF 文件路径

**返回**: `SimulationResult` - 包含解析后的 data 字典

### `parse_psf_ascii_directory(output_dir)`

解析目录中的所有 PSF ASCII 文件。

**参数**: `output_dir: Path` - Spectre 输出目录

**返回**: `dict[str, Any]` - 合并的信号数据

**自动识别的文件类型**:
- 瞬态: `tran.tran.tran`, `tran.tran`, `*.tran.tran`
- 直流: `dc.dc`, `dcOp.dc`, `spectre.dc`, `*.dc`
- 交流: `ac.ac`, `ac.ac.ac`, `*.ac.ac`
- 信息: `*.info` (操作点等)

## 输出数据格式

```python
{
    "time": [0.0, 1e-9, 2e-9, ...],      # 时间/频率数据
    "VOUT": [0.0, 0.5, 1.2, ...],        # 信号波形
    "ac_freq": [...],                     # AC 分析频率
    "ac_VOUT": [...],                     # AC 信号
}
```

## 使用示例

```python
from pathlib import Path
from virtuoso_bridge.spectre.parsers import parse_spectre_psf_ascii, parse_psf_ascii_directory

# 解析单个文件
result = parse_spectre_psf_ascii(Path("output/pss.td.pss"))
if result.ok:
    time_data = result.data["time"]
    vout = result.data["VOUT"]

# 解析整个目录
all_data = parse_psf_ascii_directory(Path("sim_output"))
tran_data = {k: v for k, v in all_data.items() if not k.startswith("ac_")}
ac_data = {k: v for k, v in all_data.items() if k.startswith("ac_")}
```
