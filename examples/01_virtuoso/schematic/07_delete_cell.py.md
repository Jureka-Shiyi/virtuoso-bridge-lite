# 关闭并删除原理图 Cell

## 功能概述

本脚本关闭当前打开的原理图窗口，然后删除整个 cell（包括所有视图）。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个原理图
python 07_delete_cell.py
```

## 代码逻辑解析

### 获取当前窗口

```python
client.execute_skill('''
let((win lib cell ddcell)
  win = car(setof(w hiGetWindowList()
              w~>cellView && w~>cellView~>viewName == "schematic"))
  unless(win return("ERROR: no schematic window open"))
  ...
''')
```

### 保存并关闭窗口

```python
dbSave(win~>cellView)
hiCloseWindow(win)
```

### 删除 Cell

```python
ddcell = ddGetObj(lib cell)
if(ddcell
  then ddDeleteObj(ddcell) sprintf(nil "deleted: %s/%s" lib cell)
  else sprintf(nil "ERROR: cell not found: %s/%s" lib cell))
```

## 警告

> **注意**：此操作会**永久删除** cell，**不可恢复**。

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso 中有打开的原理图
