# 列出 Virtuoso 库中的单元和视图

## 功能概述

本脚本提供两个功能：
1. **列出所有库名称**：不带参数运行时
2. **列出指定库中的所有单元及视图**：提供库名参数时

## 使用方法

```bash
# 列出所有库名称
python 04_list_library_cells.py

# 列出指定库中的单元和视图
python 04_list_library_cells.py MY_LIB
```

## 代码逻辑解析

### 1. 列出所有库

```python
r = client.execute_skill('''
let((out)
  out = ""
  foreach(lib ddGetLibList()
    out = strcat(out lib~>name "\\n"))
  out)
''')
```

- `ddGetLibList()` - 返回 Virtuoso 中所有库的列表
- `foreach` 遍历每个库，提取名称并拼接

### 2. 列出指定库的单元

```python
client.execute_skill(f'''
let((lib out views)
  lib = ddGetObj("{lib_name}")
  out = ""
  when(lib
    foreach(cell lib~>cells
      views = ""
      foreach(view cell~>views
        views = strcat(views view~>name " "))
      out = strcat(out sprintf(nil "%s|views=%s\\n" cell~>name views))))
  out)
''')
```

关键函数说明：
| 函数 | 作用 |
|------|------|
| `ddGetObj()` | 获取数据库对象 |
| `lib~>cells` | 获取库中的所有单元 |
| `cell~>views` | 获取单元中的所有视图 |

### 3. 解析输出

```python
for row in filter(None, decode_skill(r.output or "").splitlines()):
    cell, _, views = row.partition("|views=")
    print(f"  {cell:<20} [{views.strip()}]")
```

使用 `decode_skill()` 将 SKILL 输出解析为 Python 字符串。

## 输出格式

```
[list libraries] [0.123s]
  AnalogLib
  tsmcN28
  myDesign

[list cells] [0.456s]
  INV                    [schematic symbol]
  NAND                   [schematic symbol schematic]
  DFF                    [schematic symbol schematic layout]
```

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
