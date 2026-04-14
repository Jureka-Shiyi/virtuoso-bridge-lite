# Spectre 反相器瞬态仿真

## 功能概述

运行远程 Spectre 反相器的瞬态仿真，模拟 1GHz 脉冲驱动的 TSMC 28nm CMOS 反相器。

## 使用方法

```bash
# 默认模式 (ax)
python examples/02_spectre/01_inverter_tran.py

# 指定模式
python examples/02_spectre/01_inverter_tran.py --mode spectre
python examples/02_spectre/01_inverter_tran.py --mode aps
python examples/02_spectre/01_inverter_tran.py --mode cx
python examples/02_spectre/01_inverter_tran.py --mode ax
```

## 支持的仿真模式

| 模式 | 说明 |
|------|------|
| `spectre` | 标准 Spectre |
| `aps` | APS 扩展模式 |
| `x` | Spectre XPS |
| `cx` | Cadence Spectre |
| `ax` | Spectre APS Extended |
| `mx` | Multi-core |
| `lx` | Local MPI |
| `vx` | Vectorized |

## 电路结构

仿真的网表是一个 CMOS 反相器，由 1GHz 脉冲信号驱动。

## 代码逻辑解析

### 创建仿真器

```python
sim = SpectreSimulator.from_env(
    spectre_cmd=spectre_cmd,
    spectre_args=spectre_mode_args(mode),
    work_dir=WORK_DIR,
    output_format="psfascii",
)
```

### 运行仿真

```python
result = sim.run_simulation(NETLIST, {})
```

### 解析结果

```python
time = result.data.get("time", [])
vout = result.data.get("VOUT", [])
vin = result.data.get("VIN", [])
```

### 生成波形图

```python
_write_waveform_plot(PLOT_PATH, time, vin, vout)
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `inv_waveforms.png` | VIN/VOUT 波形图 |
| `inv_waveforms.csv` | 波形数据 CSV |
| `inv_result.json` | 仿真结果 JSON |

## 输出示例

```
[Run] Running Spectre remotely in mode 'ax' ...
[Status] ok
[Signals] ['time', 'VIN', 'VOUT']

[Preview] First 5 time points (s) and VOUT (V):
  t=0.000e+00  VOUT=1.8000
  t=1.000e-12  VOUT=1.7995
  ...

[Plot] .../output/spectre_inv/inv_waveforms.png
[CSV] .../output/spectre_inv/inv_waveforms.csv
[Summary] .../output/spectre_inv/inv_result.json
```

## 前置条件

- `.env` 配置远程 SSH 设置
- Spectre 在远程主机 PATH 中可用
- `VB_PDK_SPECTRE_INCLUDE` 指向 PDK 模型文件
