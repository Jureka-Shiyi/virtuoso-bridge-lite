# 后台打开 Maestro → 读取配置 → 关闭

## 功能概述

本脚本与 `02_gui_open_read_close_maestro.py` 类似，但使用**后台方式**打开 Maestro，不会在 GUI 中弹出窗口。

## 使用方法

```bash
python 03_bg_open_read_close_maestro.py <LIB>
```

## 代码逻辑解析

### 后台打开 session

```python
session = open_session(client, LIB, CELL)
```

`open_session()` 是专用的后台打开函数，内部使用 `maeOpenSetup()` 而非 `deOpenCellView()`。

### 读取配置

```python
for key, (skill_expr, raw) in read_config(client, session).items():
    print(f"[{key}] {skill_expr}")
    print(raw)
```

### 关闭 session

```python
close_session(client, session)
```

## GUI 打开 vs 后台打开

| 方式 | 函数 | 可见性 |
|------|------|--------|
| GUI 打开 | `deOpenCellView()` | 弹出窗口 |
| 后台打开 | `open_session()` / `maeOpenSetup()` | 不可见 |

## 适用场景

| 场景 | 推荐方式 |
|------|---------|
| 调试/查看 | GUI 打开 |
| CI/CD 自动化 | 后台打开 |
| 批量处理多个测试台 | 后台打开 |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
