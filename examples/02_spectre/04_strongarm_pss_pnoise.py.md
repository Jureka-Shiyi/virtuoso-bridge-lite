# StrongArm 比较器 PSS + Pnoise 仿真

## 功能概述

运行 StrongArm 比较器的单点 PSS（Periodic Steady-State）和 Pnoise（周期性噪声）仿真，提取关键指标并生成时域波形图。

## 使用方法

```bash
# 运行完整仿真 + 分析
python examples/02_spectre/04_strongarm_pss_pnoise.py

# 仅分析现有结果
python examples/02_spectre/04_strongarm_pss_pnoise.py --analyze-only
```

## 电路说明

StrongArm 比较器是一种高速低噪声比较器架构，常用于 ADC 中。

仿真参数：
- **Vcm**: 0.45V（共模电压）

## 代码逻辑解析

### 构建网表

```python
def _build_netlist(base_text: str, vcm: float) -> str:
    lines_out = []
    for line in base_text.splitlines():
        if stripped.startswith("parameters ") and "Vcm=" in stripped:
            # 替换 Vcm 参数
            lines_out.append(
                " ".join(f"Vcm={vcm:.4f}" if part.startswith("Vcm=") else part
                         for part in parts)
            )
        else:
            lines_out.append(line)
    return "\n".join(lines_out)
```

### PSS + Pnoise 仿真

```python
sim = SpectreSimulator.from_env(
    spectre_cmd=os.getenv("SPECTRE_CMD", "spectre"),
    spectre_args=spectre_mode_args("ax"),
    work_dir=OUT_DIR,
    output_format="psfascii",
)
result = sim.run_simulation(RUN_NETLIST, {})
```

### 提取指标

```python
metrics = extract_metrics(raw_dir, vcm=vcm)
```

指标包括（来自 `analyze_strongarm_pss_pnoise.py`）：
- 传播延迟
- 失调电压
- 噪声指标
- 等

### 生成时域图

```python
plot_path = write_time_domain_plot(raw_dir, PLOT_PATH)
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `tb_cmp_strongarm_run.scs` | 运行网表 |
| `strongarm_pss_pnoise_metrics.json` | 提取的指标 JSON |
| `strongarm_pss_pnoise_result.json` | 仿真结果摘要 |
| `strongarm_pss_time_domain.png` | 时域波形图 |

## 输出示例

```
Vcm : 0.450 V

[Run] Running StrongArm single-point PSS + Pnoise remotely ...
Status : ok
Errors : 0
Warnings : 2

Metrics:
  propagation_delay: 2.3e-12
  input_referred_offset: 1.5e-3
  ...

[Metrics] .../output/strongarm_pss_pnoise/strongarm_pss_pnoise_metrics.json
[Plot] .../output/strongarm_pss_pnoise/strongarm_pss_time_domain.png
[Summary] .../output/strongarm_pss_pnoise/strongarm_pss_pnoise_result.json
```

## 分析模块

`assets/strongarm_cmp/analyze_strongarm_pss_pnoise.py` 提供：
- `extract_metrics()` - 从仿真结果提取指标
- `write_time_domain_plot()` - 生成时域波形图

## 前置条件

- `.env` 配置远程 SSH 设置
- Spectre 在远程可用
- StrongArm 比较器网表存在
