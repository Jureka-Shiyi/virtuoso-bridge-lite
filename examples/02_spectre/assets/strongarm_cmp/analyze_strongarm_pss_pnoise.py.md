# StrongArm 比较器 PSS + Pnoise 分析工具

## 功能概述

分析 StrongArm 比较器的 PSS（周期性稳态）和 Pnoise（周期性噪声）仿真结果，提取关键性能指标。

## 电路参数

| 参数 | 值 |
|------|-----|
| VDD | 0.9V |
| 目标传播延迟 (Tcmp) | < 50ps |
| 目标噪声 (Noise) | < 400µVrms |

## 核心函数

### `parse_psf()`

```python
def parse_psf(path: Path) -> dict[str, np.ndarray]:
    from virtuoso_bridge.spectre.parsers import parse_spectre_psf_ascii
    result = parse_spectre_psf_ascii(path)
    return {key: np.asarray(values, dtype=float) for key, values in result.data.items()}
```

解析 Spectre PSF 格式的仿真输出文件。

### `first_crossing()`

```python
def first_crossing(time_values, signal_values, level, direction="rising") -> float | None:
    """找到信号首次穿越指定电平的时间点"""
```

关键参数：
- `level`: 目标电平 (VDD/2 = 0.45V)
- `direction`: `"rising"` 或 `"falling"`

### `extract_metrics()`

```python
def extract_metrics(raw_dir: Path, *, vcm: float) -> dict:
    # 解析 PSF 文件
    pss = parse_psf(pss_td)
    pnoise = parse_psf(pnoise_file)

    # 计算平均电流和功耗
    period = float(time_values[-1] - time_values[0])
    avg_current = float(_trapz(supply_current, time_values)) / period
    power_uW = -avg_current * VDD * 1e6

    # 计算传播延迟
    diff = dcmpn - dcmpp
    tcmp_raw = first_crossing(time_values, diff, VDD/2, "rising")

    # 计算 RMS 噪声 (0-500MHz)
    mask = (freq >= 0.0) & (freq <= 500e6)
    noise_rms = float(np.sqrt(_trapz(noise_out[mask] ** 2, freq[mask]))) / 50.0

    # 计算 FOM
    fom1 = noise_rms**2 * (power_uW * 1e-6) * 1e12
    fom2_u = noise_rms**2 * (power_uW * 1e-6) * tcmp * 1e18 * 1e6
```

## 提取的指标

| 指标 | 说明 | 单位 |
|------|------|------|
| `vcm` | 共模电压 | V |
| `power_uW` | 平均功耗 | µW |
| `Tcmp_ps` | 传播延迟 | ps |
| `Tcmprst_ps` | 重置延迟 | ps |
| `Noise_uVrms` | 输入参考噪声 | µVrms |
| `FOM1` | 品质因数 1 | - |
| `FOM2_u` | 品质因数 2 (含延迟) | - |
| `pass_Tcmp` | 延迟是否达标 | bool |
| `pass_Noise` | 噪声是否达标 | bool |

## FOM 计算公式

**FOM1** (仅噪声和功耗)：
```
FOM1 = Noise² × Power × 1e12
```

**FOM2** (含传播延迟)：
```
FOM2 = Noise² × Power × Tcmp × 1e24
```

## `write_time_domain_plot()`

绘制 PSS 时域波形：
- 子图1: 时钟 (CLK)、正负输入 (VINP, VINN)
- 子图2: Latch 节点 (LP, LM)
- 子图3: 缓冲输出 (DCMPP, DCMPN)

## 使用方法

```python
from analyze_strongarm_pss_pnoise import extract_metrics, write_time_domain_plot

# 提取指标
metrics = extract_metrics(raw_dir, vcm=0.45)
print(f"传播延迟: {metrics['Tcmp_ps']:.2f} ps")
print(f"功耗: {metrics['power_uW']:.2f} µW")
print(f"噪声: {metrics['Noise_uVrms']:.2f} µVrms")

# 绘制波形
plot_path = write_time_domain_plot(raw_dir, Path("output.png"))
```

## 数据文件

| 文件 | 说明 |
|------|------|
| `pss.td.pss` | PSS 时域输出 |
| `pnoiseMpm0.0.sample.pnoise` | 噪声分析输出 |
