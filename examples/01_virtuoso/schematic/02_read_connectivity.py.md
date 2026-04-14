# 读取原理图连接关系

## 功能概述

本脚本从原理图中读取完整的连接信息，包括：
- 实例列表（名称、库、单元）
- 网络列表（名称、连接关系）
- 引脚列表（名称、方向）

## 使用方法

```bash
# 指定库和单元
python 02_read_connectivity.py MYLIB MYCELL

# 使用当前打开的设计
python 02_read_connectivity.py
```

## 代码逻辑解析

### 读取连接

```python
data = read_connectivity(client, lib, cell)
```

### 格式化输出

```python
def format_connectivity(data: dict) -> str:
    instances = data.get("instances", [])
    nets = data.get("nets", [])
    pins = data.get("pins", [])

    # 打印实例
    for i in instances:
        print(f"{i['name']:<{name_w}}  {i['lib']}/{i['cell']}")

    # 打印网络
    for n in nets:
        print(f"{n['name']:<{net_w}}  {'  '.join(n['connections'])}")

    # 打印引脚
    for p in pins:
        print(f"{p['name']:<{pin_w}}  {p['direction']}")
```

## 输出格式示例

```
Instances : 3   Nets : 4   Pins : 3

INSTANCE              LIB/CELL
------------------------------------
V0                   analogLib/vdc
R0                   analogLib/res
C0                   analogLib/cap

NET                  CONNECTIONS (inst.terminal)
-------------------------------------------------------
VDD                  V0.PLUS
GND                  V0.MINUS  C0.MINUS
OUT                  R0.MINUS  C0.PLUS

PIN                  DIRECTION
----------------------------------------
VIN                  INPUT
VOUT                 OUTPUT
```

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
