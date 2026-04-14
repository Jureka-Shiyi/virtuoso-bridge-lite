# 读取 Maestro 环境设置

## 功能概述

本脚本从已打开的 Maestro 窗口读取环境设置，包括：
- 模型文件路径
- 仿真选项
- 运行模式

## 使用方法

1. 在 Virtuoso GUI 中打开一个 Maestro 视图
2. 运行脚本

```bash
python 04_read_env.py
```

## 代码逻辑解析

### 查找打开的 session

```python
session = find_open_session(client)
if session is None:
    print("No active maestro session found.")
    return 1
```

### 读取环境

```python
for key, (skill_expr, raw) in read_env(client, session).items():
    print(f"[{key}] {skill_expr}")
    print(raw)
```

## 返回的环境信息

| Key | 说明 |
|-----|------|
| `modelFiles` | 加载的模型文件 |
| `simOptions` | 仿真选项 |
| `runMode` | 运行模式 |
| `path` | 设计库路径 |

## 适用场景

- 验证仿真环境配置
- 检查模型文件是否正确加载
- 调试仿真设置问题

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso GUI 中有打开的 Maestro 窗口
