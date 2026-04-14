# Verilog-A ADC/DAC 仿真

## 功能概述

运行捆绑的 Verilog-A ADC/DAC 测试平台，支持正弦波和斜坡两种测试用例。

## 使用方法

```bash
# 默认正弦波测试
python examples/02_spectre/01_veriloga_adc_dac.py

# 指定测试用例
python examples/02_spectre/01_veriloga_adc_dac.py --case sine
python examples/02_spectre/01_veriloga_adc_dac.py --case ramp

# 指定仿真模式
python examples/02_spectre/01_veriloga_adc_dac.py --case sine --mode ax
```

## 测试用例

### Sine (正弦波)

| 配置 | 说明 |
|------|------|
| 网表 | `tb_adc_dac_ideal_4b_sine.scs` |
| Verilog-A | `adc_ideal_4b.va`, `dac_ideal_4b.va`, `sh_ideal.va` |

### Ramp (斜坡)

| 配置 | 说明 |
|------|------|
| 网表 | `tb_adc_dac_ideal_4b_ramp.scs` |
| Verilog-A | `adc_ideal_4b.va`, `dac_ideal_4b.va` |

## 电路结构

4 位理想 ADC/DAC：
- 输入：Vin (模拟信号)
- ADC：将模拟信号转换为 4 位数字码
- DAC：将数字码转换回模拟信号
- 输出：Vout

## 代码逻辑解析

### 波形绘图

**Sine 测试绘图**：
```python
fig, axes = plt.subplots(3, 1, ...)
# 子图1: vin, vin_sh, vout 电压
# 子图2: ADC 码值
# 子图3: vout - vin_sh 误差 (mV)
```

**Ramp 测试绘图**：
```python
fig, axes = plt.subplots(3, 1, ...)
# 子图1: clk 时钟
# 子图2: vin, vout 电压
# 子图3: ADC 码值
```

### 位值提取

```python
def _bit_values(data: dict[str, list[float]], bit: int) -> list[float]:
    return data.get(f"dout_{bit}", [])

# 组合成完整码值
code = np.zeros_like(time_ns, dtype=int)
for bit in range(4):
    code += np.rint(np.asarray(_bit_values(data, bit), dtype=float)).astype(int) << bit
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `adc_dac_ideal_4b_*.png` | 波形图 |
| `adc_dac_ideal_4b_*.csv` | 波形数据 CSV |
| `adc_dac_ideal_4b_*_result.json` | 结果 JSON |

## 前置条件

- `.env` 配置远程 SSH 设置
- Spectre 在远程可用
- Verilog-A 文件存在
