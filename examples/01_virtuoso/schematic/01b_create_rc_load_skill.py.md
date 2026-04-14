# 创建 RC 滤波器原理图（简化版）

## 功能概述

与 `01a_create_rc_stepwise.py` 功能相同，但使用简化写法，电路结构一致。

**电路结构**：
```
VDC → R1 (res) → VOUT → C1 (cap) → GND
```

## 与 01a 的对比

| 特性 | 01a | 01b |
|------|-----|-----|
| 电路 | V0 + R0 + C0 | V1 + R1 + C1 |
| 网络名 | VDD, OUT, GND | VIN, VOUT, GND |
| 功能 | 完全相同 | 完全相同 |

## 代码逻辑解析

### 创建实例和标签

```python
with client.schematic.edit(lib, cell) as sch:
    sch.add(inst("analogLib", "vdc", "symbol", "V1", 0.0, 0.0, "R0"))
    sch.add(inst("analogLib", "res", "symbol", "R1", 1.0, 0.5, "R0"))
    sch.add(inst("analogLib", "cap", "symbol", "C1", 2.0, 0.0, "R0"))

    sch.add(label_term("V1", "PLUS",  "VIN"))
    sch.add(label_term("V1", "MINUS", "GND"))
    sch.add(label_term("R1", "PLUS",  "VIN"))
    sch.add(label_term("R1", "MINUS", "VOUT"))
    sch.add(label_term("C1", "PLUS",  "VOUT"))
    sch.add(label_term("C1", "MINUS", "GND"))
```

## 输出结果

```
Created myLib/tmp_20260414_103000/schematic  (V1:vdc  R1:res  C1:cap  nets: VIN VOUT GND)
```

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
