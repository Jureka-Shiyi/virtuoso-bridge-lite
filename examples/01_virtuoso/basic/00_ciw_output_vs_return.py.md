# CIW 输出 vs Python 返回值

## 功能概述

本示例演示了 `execute_skill()` 方法的**两个关键概念**：

1. **Python 返回值**：SKILL 表达式的执行结果会返回给 Python
2. **CIW 输出**：结果**不会**自动打印到 Virtuoso CIW 窗口

## 核心知识点

### 1. 为什么 `execute_skill()` 不会在 CIW 中显示结果？

`execute_skill()` 是一个远程过程调用（RPC）机制：
- 它将 SKILL 代码发送到远程 Virtuoso 执行
- 将执行结果**返回**给 Python 端
- **不会**自动调用 `printf()` 在 CIW 中打印

### 2. 如何同时获取返回值和 CIW 输出？

使用 `let()` 表达式同时完成两件事：
```python
r = client.execute_skill(r'let((v) v=1+2 printf("1+2 = %d\n" v) v)')
```

- `printf("1+2 = %d\n" v)` → 输出到 CIW
- `v`（let 的最后一个表达式）→ 返回给 Python

## 输出对比

| 调用方式 | Python console | CIW window |
|---------|---------------|------------|
| `client.execute_skill("1+2")` | 显示 `3` | 无输出 |
| `let((v) v=1+2 printf(...))` | 显示 `3` | 显示 `1+2 = 3` |

## 代码逻辑

```python
# 仅返回，无 CIW 输出
r = client.execute_skill("1+2")
print(f"[Python] 1+2 = {r.output}")

# 返回值 + CIW 输出
r = client.execute_skill(r'let((v) v=1+2 printf("1+2 = %d\n" v) v)')
print(f"[Python] 1+2 = {r.output}")
```

## 关键结论

> **重要**：如果你需要在 CIW 中看到调试信息，必须显式调用 `printf()`。仅靠 `execute_skill()` 的返回值是不会在 CIW 中显示的。

## 相关示例

- `02_ciw_print.py` - 使用 `printf()` 在 CIW 中打印多行内容
- `03_load_il.py` - 通过加载 .il 文件间接实现 CIW 输出
