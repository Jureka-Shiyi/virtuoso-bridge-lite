# RC 滤波器 DC + AC 仿真

## 功能概述

在 RC 低通滤波器上运行 DC 工作点和 AC 频率响应仿真，计算 -3dB 截止频率并与理论值对比。

## 使用方法

```bash
python examples/02_spectre/02_cap_dc_ac.py
```

## 电路结构

```
         VDD ──┬── R0 (1K) ──┬── VO ──┬── C1 (50f) ──┬── GND
                │             │        │              │
                │             │        │              │
               C0 (50f)      GND      GND            GND
               (ref)
```

**理论计算**：
- f_3dB = 1 / (2π × R × C)
- f_3dB = 1 / (2π × 1e3 × 50e-15) ≈ 3.18 GHz

## 代码逻辑解析

### DC 工作点

```python
dc_vdd = result.data.get("dc_VDD")
dc_vo = result.data.get("dc_VO")
print(f"  VDD = {dc_vdd:.4f} V")
print(f"  VO  = {dc_vo:.4f} V")
```

### AC 频率响应

```python
freq = result.data.get("ac_freq", [])
vo_mag = result.data.get("ac_VO", [])

# 转换为 dB
vo_db = [20 * math.log10(max(v, 1e-30)) for v in vo_mag]

# 找 -3dB 点
for i, db in enumerate(vo_db):
    if db <= -3.0:
        # 线性插值
        f_3dB = freq[i - 1] + (freq[i] - freq[i - 1]) * (-3.0 - vo_db[i - 1]) / (vo_db[i] - vo_db[i - 1])
        break
```

### 从 AC 电流提取电容

```python
i_cap = result.data.get("ac_C0:1", [])
cap_val = di / df / (2 * math.pi)
```

利用 X = 1/(jωC) 关系从电流计算电容值。

### 绘制伯德图

```python
def _write_plot(freq, vo_db, f_3dB, out_path):
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=160)
    ax.semilogx(freq_ghz, vo_db, ...)
    ax.axhline(-3, ...)  # -3dB 线
    if f_3dB:
        ax.axvline(f_3dB / 1e9, ...)  # 截止频率线
```

## 输出示例

```
DC operating point:
  VDD = 1.8000 V
  VO  = 0.9000 V

AC frequency response:
  Sweep: 1.00e+02 – 1.00e+12 Hz (100 points)
  |VO| at 1.00e+02 Hz: 1.0000 (0.0 dB)
  |VO| at 1.00e+12 Hz: 0.0001 (-80.0 dB)
  f_3dB = 3.183e+09 Hz (3.18 GHz)
  Expected f_3dB = 3.183e+09 Hz (3.18 GHz)

C0 capacitance (from AC current at 1.00e+08 Hz):
  C = 50.23 fF

Plot saved: .../cap_dc_ac/rc_filter_ac_response.png
```

## 前置条件

- `.env` 配置远程 SSH 设置
- Spectre 在远程可用
- 网表文件存在
