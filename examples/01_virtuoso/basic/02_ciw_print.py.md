# 在 CIW 中打印莎士比亚十四行诗

## 功能概述

本示例演示如何通过 `execute_skill()` 在 Virtuoso CIW 窗口中打印**多行文本**。

关键点：每行必须作为单独的 `printf()` 调用，因为多行 `printf()` 会丢失换行符。

## 核心问题：为什么不能批量 printf？

```python
# 错误做法：所有内容在一行
client.execute_skill('printf("line1\nline2\nline3")')

# 正确做法：每行单独调用
for line in sonnet.splitlines():
    client.execute_skill(f'printf("{line}\\n")')
```

## 实现方式

### 逐行打印

```python
sonnet = """\
========================================================
  Sonnet 18  by William Shakespeare
========================================================
  Shall I compare thee to a summer's day?
..."""

for line in sonnet.splitlines():
    r = client.execute_skill('printf("' + line + '\\n")')
    if r.status.value != "success":
        print(f"Error: {r.errors}")
```

### 字符串转义处理

在构建 SKILL 命令时需要注意引号转义：
- Python 字符串中的 `"` 需要写成 `\"`
- 换行符 `\n` 需要写成 `\\n`

## 输出效果

执行后，在 Virtuoso CIW 窗口中会看到格式化的十四行诗：

```
========================================================
  Sonnet 18  by William Shakespeare
========================================================
  Shall I compare thee to a summer's day?
  Thou art more lovely and more temperate:
  ...
========================================================
```

## 与 03_load_il.py 的对比

| 方法 | 优点 | 缺点 |
|------|------|------|
| `02_ciw_print.py` (逐行 printf) | 简单直接 | 网络往返次数多 |
| `03_load_il.py` (加载 .il 文件) | 一次网络往返 | 需要额外的 IL 文件 |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW

## 适用场景

- 调试时打印中间变量
- 在 CIW 中显示状态信息
- 格式化输出设计检查结果
