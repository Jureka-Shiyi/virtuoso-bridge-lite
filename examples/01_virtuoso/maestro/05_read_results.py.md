# 读取仿真结果

## 功能概述

本脚本从已运行仿真的 Maestro 会话中读取仿真结果，包括：
- 输出值
- 规格检查结果
- 整体 yield

## 使用方法

1. 在 Virtuoso GUI 中打开一个 Maestro 视图（**必须已运行过仿真**）
2. 运行脚本

```bash
python 05_read_results.py
```

## 代码逻辑解析

### 查找 session

```python
session = find_open_session(client)
if session is None:
    print("No active maestro session found.")
    return 1
```

### 读取结果

```python
results = read_results(client, session)
if not results:
    print("No simulation results found.")
    return 1

for key, (skill_expr, raw) in results.items():
    print(f"[{key}] {skill_expr}")
    print(raw)
```

## 返回结果类型

| Key | 说明 | 示例 |
|-----|------|------|
| `outputs` | 输出值 | `VOUT = 0.8V` |
| `specs` | 规格通过/失败 | `PASS/FAIL` |
| `yield` | 整体良率 | `100%` |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso GUI 中有已运行过仿真的 Maestro 窗口
