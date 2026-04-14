# 通过 spiceIn 导入 CDL 电容阵列

## 功能概述

本脚本生成一个 4 位二进制加权电容阵列的 CDL 网表，通过 SSH 运行 `spiceIn` 导入到 Virtuoso，自动创建原理图和布线。

## 电路结构

```
单个电容单元: cap_unit (TOP, BOT)
4位电容阵列:  cap_array_4b
  - 位权重: [1, 2, 4, 8] (对应 15 个单位电容)
  - 引脚: TOP, BOT<3:0>
```

## 使用方法

```bash
python 08_import_cdl_cap_array.py <LIB>
```

## 代码逻辑解析

### 生成 CDL 网表

```cdl
.SUBCKT cap_unit TOP BOT
C0 TOP BOT cap C=1.0000e-14
.ENDS

.SUBCKT cap_array_4b TOP BOT<3:0>
XC_b0_0 TOP BOT<0> cap_unit        ; 1 unit
XC_b1_0 TOP BOT<1> cap_unit        ; 2 units
XC_b1_1 TOP BOT<1> cap_unit
XC_b2_0 TOP BOT<2> cap_unit        ; 4 units
...                              ; 共 15 units
XC_b3_7 TOP BOT<3> cap_unit
.ENDS
```

### 通过 SSH 运行 spiceIn

```python
# 关键：spiceIn 必须通过 SSH 运行，不能通过 SKILL system()
# 因为 system() 会启动内部 Virtuoso 进程，导致 CIW 死锁

result = subprocess.run(
    _ssh_cmd(client) + [f"bash {script_path}"],
    capture_output=True, text=True, timeout=120,
)
```

### 创建 Symbol

```python
client.execute_skill(
    f'schPinListToSymbol("{LIB}" "cap_unit" "symbol" '
    f'schSchemToPinList("{LIB}" "cap_unit" "schematic"))')
```

## 重要注意事项

> **警告**：`spiceIn` 必须通过 SSH 运行，绝不能通过 SKILL 的 `system()` 调用。因为 `system()` 会启动内部 Virtuoso 进程，导致 CIW 死锁。

## 关键路径发现

```python
# 从运行中的 Virtuoso 发现路径
r = client.execute_skill('cdsGetInstPath()')
cds_inst = r.output.strip('"')
spicein = f"{cds_inst}/bin/spiceIn"
```

## 前置条件

- `virtuoso-bridge start` 已运行
- spiceIn 工具在远程可用
- SSH 访问远程主机
