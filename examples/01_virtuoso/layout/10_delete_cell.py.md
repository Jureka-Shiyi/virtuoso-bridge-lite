# 关闭并删除当前布局 Cell

## 功能概述

本示例展示如何：
1. 关闭当前打开的 layout cellview
2. 删除整个 cell（包括所有视图）

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 10_delete_cell.py
```

## 代码逻辑解析

### 步骤 1: 获取当前设计

```python
lib, cell, view = client.get_current_design()
if not lib or view != "layout":
    print("No active layout window.")
    return 1
```

### 步骤 2: 关闭 Cellview

```python
close_result = client.close_current_cellview(timeout=15)
if close_result.ok:
    print(f"[close_current_cellview] [{format_elapsed(close_elapsed)}]")
else:
    print(f"[close_current_cellview] failed: {errors[0]}")
```

### 步骤 3: 删除 Cell

```python
result = client.layout.delete_cell(lib, cell, timeout=30)
print(f"[layout.delete_cell] [{format_elapsed(delete_elapsed)}]")
print(decode_skill(result.output or ""))
```

## 删除操作 API

```python
client.layout.delete_cell(lib, cell, timeout=30)
```

## 警告

> **注意**：此操作会**永久删除** cell，**不可恢复**。请确保已备份重要数据。

## 适用场景

- 清理测试创建的临时 cells
- 批量删除旧版本 cells
- CI/CD 流程中的清理步骤

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
