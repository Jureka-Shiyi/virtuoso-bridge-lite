# 读取原理图实例 CDF 参数

## 功能概述

本脚本从原理图中读取实例的 CDF (Component Description Format) 参数，如晶体管的 W、L、NF 等。

## 使用方法

```bash
# 读取当前原理图的所有参数
python 03_read_instance_params.py

# 读取指定库的指定单元
python 03_read_instance_params.py MYLIB MYCELL

# 只读取特定参数
python 03_read_instance_params.py MYLIB MYCELL --filter w l nf m
```

## 参数过滤

```python
if "--filter" in argv:
    filter_names = argv[idx + 1:]

params = read_instance_params(client, lib, cell, filter_params=filter_names)
```

## 输出格式

```
Reading myLib/myCell/schematic ...

NMOS0  [technology/nch]
  w = 1.0u
  l = 28n
  nf = 1
  m = 1

NMOS1  [technology/nch]
  w = 2.0u
  l = 28n
  nf = 2
  m = 2
```

## 常用 CDF 参数

| 器件类型 | 常见参数 |
|---------|---------|
| MOS | w, l, nf, m, ad, as, pd, ps |
| 电阻 | r, w, l, temp |
| 电容 | c, w, l, m |
| 电感 | l, w, m |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
