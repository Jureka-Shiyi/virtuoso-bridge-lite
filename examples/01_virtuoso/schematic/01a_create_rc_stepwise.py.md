# 逐步创建 RC 低通滤波器原理图

## 功能概述

使用 Python SchematicEditor API 创建 RC 低通滤波器电路。

**电路结构**：
```
VDC (0.8V) → R0 (res) → OUT → C0 (cap) → GND
```

## 使用方法

```bash
python 01a_create_rc_stepwise.py <LIB>
```

## 电路图

```
        ┌─────────┐
   ┌────┤ R0      ├────┬────┤ C0    ├──── GND
   │    └─────────┘    │    └─────────┘
   │                  │
   │                  ▼
  VDD                OUT
   │                  │
   │                  │
   └──────────────────┘
```

## 代码逻辑解析

### 创建实例

```python
with client.schematic.edit(lib, cell) as sch:
    sch.add(inst("analogLib", "vdc", "symbol", "V0", 3.0, 0.0, "R0"))
    sch.add(inst("analogLib", "res", "symbol", "R0", 0.0, 0.0, "R0"))
    sch.add(inst("analogLib", "cap", "symbol", "C0", 1.5, 0.0, "R0"))
```

### 添加网络标签

```python
sch.add(label_term("V0", "PLUS",  "VDD"))
sch.add(label_term("V0", "MINUS", "GND"))
sch.add(label_term("R0", "PLUS",  "VDD"))
sch.add(label_term("R0", "MINUS", "OUT"))
sch.add(label_term("C0", "PLUS",  "OUT"))
sch.add(label_term("C0", "MINUS", "GND"))
```

### 设置 CDF 参数

```python
client.execute_skill(
    'schHiReplace(?replaceAll t ?propName "cellName" ?condOp "==" '
    '?propValue "vdc" ?newPropName "vdc" ?newPropValue "800m")')
```

使用 `schHiReplace()` 设置参数值，而非直接修改 `param~>value`。

## SchematicEditor API

| 函数 | 作用 |
|------|------|
| `sch.add()` | 添加元素 |
| `schematic_create_inst_by_master_name` | 创建实例 |
| `schematic_label_instance_term` | 添加网络标签 |

## 关键规则

> **重要**：设置 CDF 参数应使用 `schHiReplace()`，而非直接设置 `param~>value`。设置后需调用 `CCSinvokeCdfCallbacks()` 触发回调更新。

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
