# 创建 RC 滤波器原理图 + Maestro 设置

## 功能概述

这是两步流程的第一步，创建：
1. **原理图**：VDC (AC=1) → R (1k) → C (c_val) → GND，带 OUT 引脚
2. **Maestro 设置**：AC 分析 1Hz–10GHz，扫描 c_val = 1p, 100f，带宽规格 > 1GHz

## 使用方法

```bash
# 先创建原理图和 Maestro 设置
python 06a_rc_create.py <LIB>

# 然后运行仿真（第二步）
python 06b_rc_simulate_and_read.py <LIB>
```

## 创建的电路

```
VDC (AC=1)
    │
    ├──► R0 (1k) ──┬──► C0 (c_val) ──► OUT
    │              │
    │              │
   GND            GND
```

## 代码逻辑解析

### 创建原理图

```python
with client.schematic.edit(LIB, CELL) as sch:
    sch.add(inst("analogLib", "vdc", "symbol", "V0", 0, 0, "R0"))
    sch.add(inst("analogLib", "gnd", "symbol", "GND0", 0, -0.625, "R0"))
    sch.add(inst("analogLib", "res", "symbol", "R0", 1.5, 0.5, "R90"))
    sch.add(inst("analogLib", "cap", "symbol", "C0", 3.0, 0, "R0"))
    sch.add(inst("analogLib", "gnd", "symbol", "GND1", 3.0, -0.625, "R0"))

    sch.add(wire("V0", "PLUS", "R0", "PLUS"))
    sch.add(wire("R0", "MINUS", "C0", "PLUS"))
    sch.add(wire("C0", "MINUS", "GND1", "gnd!"))
    sch.add(wire("V0", "MINUS", "GND0", "gnd!"))
    sch.add(pin_at("C0", "PLUS", "OUT"))
```

### 设置 CDF 参数

```python
for inst, param, val in [("V0", "vdc", "0"), ("V0", "acm", "1"),
                          ("R0", "r", "1k"), ("C0", "c", "c_val")]:
    client.execute_skill(...)
```

| 实例 | 参数 | 值 |
|------|------|-----|
| V0 | vdc | 0 |
| V0 | acm | 1 (AC magnitude) |
| R0 | r | 1k |
| C0 | c | c_val (变量) |

### 创建 Maestro 设置

```python
session = open_session(client, LIB, CELL)

create_test(client, "AC", lib=LIB, cell=CELL, session=session)
set_analysis(client, "AC", "ac",
             options='(("start" "1") ("stop" "10G") ...)',
             session=session)
add_output(client, "Vout", "AC", ...)
add_output(client, "BW", "AC", ...)
set_spec(client, "BW", "AC", gt="1G", session=session)
set_var(client, "c_val", "1p,100f", session=session)

save_setup(client, LIB, CELL, session=session)
close_session(client, session)
```

## Maestro API

| 函数 | 作用 |
|------|------|
| `create_test()` | 创建测试 |
| `set_analysis()` | 设置分析类型 |
| `add_output()` | 添加输出表达式 |
| `set_spec()` | 设置规格 |
| `set_var()` | 设置变量 |
| `save_setup()` | 保存设置 |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
