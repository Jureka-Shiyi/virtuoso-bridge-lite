# ADC/DAC 4位理想转换器分析工具

## 功能概述

分析 4 位理想 ADC → DAC 闭环转换结果，支持斜坡 (ramp) 和正弦 (sine) 两种输入信号。

## 电路说明

4 位理想 ADC/DAC 系统：
- **ADC**: 将模拟输入转换为 4 位数字码 (0-15)
- **DAC**: 将数字码转换回模拟电压
- **VDD**: 0.9V
- **分辨率**: 1 LSB = VDD/16 = 56.25mV

## 核心函数

### `analyze()`

```python
def analyze(out_dir: Path = _DEFAULT_OUT) -> None:
    # 1. Ramp 测试
    _plot_ramp(out_ramp, wall_ramp)

    # 2. Sine 测试 (63 samples/cycle)
    _plot_sine(out_sine, wall_sine, 63, 'analyze_sine.png')

    # 3. Sine 测试 (1000 samples/cycle)
    _plot_sine(out_sine1000, wall_sine1000, 1000, 'analyze_sine1000.png')
```

### `_plot_ramp()`

绘制斜坡输入测试结果：
- 子图1: 时钟信号
- 子图2: 输入斜坡电压
- 子图3: ADC 码值 + DAC 输出电压

### `_plot_sine()`

绘制正弦输入测试结果：
- 子图1: 输入正弦、S&H 保持电压、DAC 输出
- 子图2: ADC 数字码
- 子图3: 量化误差 (vin_sh - vout)

## 关键指标

| 指标 | 说明 |
|------|------|
| LSB | 1 LSB = 56.25mV |
| 码值范围 | 0-15 |
| 量化误差 | 应在 ±1 LSB 内 |

## 输出文件

| 文件 | 说明 |
|------|------|
| `ramp/analyze_ramp.png` | 斜坡测试波形图 |
| `sine/analyze_sine.png` | 正弦测试波形图 (63 samples/cycle) |
| `sine1000/analyze_sine1000.png` | 正弦测试波形图 (1000 samples/cycle) |

## 使用方法

```bash
# 直接运行（使用默认输出目录）
python analyze_adc_dac_ideal_4b.py

# 指定输出目录
python analyze_adc_dac_ideal_4b.py --out-dir /path/to/output
```

## 依赖

- `matplotlib` - 绘图
- `numpy` - 数据处理
- `evas.netlist.runner.evas_simulate` - 网表仿真

## 注意事项

- 斜坡测试等待 12ns 稳定时间
- 正弦测试等待 3ns 稳定时间
- 转换器是理想的，量化误差应完全由分辨率决定
