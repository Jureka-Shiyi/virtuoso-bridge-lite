# 清除当前布局所有内容

## 功能概述

本示例演示如何清除当前布局窗口中**所有可见的图形**（shapes、instances、labels 等）。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 09_clear_current_layout.py
```

## 代码逻辑解析

### 调用清除

```python
result = client.layout.clear_current(timeout=30)
print(f"[layout.clear_current] [{format_elapsed(elapsed)}]")

output = decode_skill(result.output or "")
if output:
    print(output)
for error in result.errors or []:
    print(f"[error] {error}")
```

## 警告

> **注意**：`clear_current()` 会删除**所有**图形，包括 instances。这个操作**不可逆**。

## 与其他清除操作的对比

| 函数 | 作用 | 保留实例 |
|------|------|---------|
| `clear_current()` | 清除所有可见图元 | **否** |
| `clear_routing()` | 清除所有走线 shapes | 是 |
| `delete_shapes_on_layer()` | 清除指定层 | 是 |

## 适用场景

- 清理测试用布局
- 重新开始设计
- 批量操作前的初始化

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
