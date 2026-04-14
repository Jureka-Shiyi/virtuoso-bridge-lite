# 读取已打开的 Maestro 配置

## 功能概述

本脚本从当前打开的 Virtuoso Maestro 窗口中读取配置信息，**不会**打开或关闭任何窗口。

## 使用方法

1. 在 Virtuoso GUI 中打开一个 maestro 视图
2. 运行脚本

```bash
python 01_read_open_maestro.py
```

## 代码逻辑解析

### 查找打开的 session

```python
session = find_open_session(client)
if session is None:
    print("No active maestro session found.")
    return 1
```

### 读取配置

```python
for key, (skill_expr, raw) in read_config(client, session).items():
    print(f"[{key}] {skill_expr}")
    print(raw)
```

## 返回的配置文件信息

| Key | 说明 |
|-----|------|
| `tests` | 测试列表 |
| `analyses` | 分析设置 |
| `variables` | 变量设置 |
| `outputs` | 输出设置 |
| `specs` | 规格限制 |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso GUI 中有打开的 Maestro 窗口
