# 数据模型

## 功能概述

定义 Virtuoso bridge 的核心数据模型，包括执行结果、仿真结果和抽象接口。

## ExecutionStatus 枚举

执行状态枚举。

| 状态 | 说明 |
|------|------|
| `SUCCESS` | 执行成功 |
| `FAILURE` | 执行失败 |
| `PARTIAL` | 部分成功（有输出但有问题） |
| `ERROR` | 执行错误 |

## VirtuosoResult 类

SKILL 命令执行结果。

| 属性 | 类型 | 说明 |
|------|------|------|
| `status` | `ExecutionStatus` | 执行状态 |
| `output` | `str` | 命令输出 |
| `errors` | `list[str]` | 错误列表 |
| `warnings` | `list[str]` | 警告列表 |
| `execution_time` | `float \| None` | 执行时间（秒） |
| `metadata` | `dict[str, Any]` | 元数据 |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `ok` | `bool` | 是否成功（status == SUCCESS） |

### 方法

| 方法 | 说明 |
|------|------|
| `save_json(path)` | 将结果写入 JSON 文件 |

## SimulationResult 类

Spectre 仿真结果。

| 属性 | 类型 | 说明 |
|------|------|------|
| `status` | `ExecutionStatus` | 仿真状态 |
| `tool_version` | `str \| None` | 工具版本 |
| `data` | `dict[str, Any]` | 解析后的波形数据 |
| `errors` | `list[str]` | 错误列表 |
| `warnings` | `list[str]` | 警告列表 |
| `metadata` | `dict[str, Any]` | 元数据（包含 timings、output_dir 等） |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `ok` | `bool` | 是否成功 |

### 方法

| 方法 | 说明 |
|------|------|
| `save_json(path)` | 将结果写入 JSON 文件 |

## VirtuosoInterface 抽象类

Virtuoso SKILL 执行的抽象接口。

| 方法 | 说明 |
|------|------|
| `ensure_ready(timeout)` | 确保 bridge 就绪 |
| `execute_skill(skill_code, timeout)` | 执行 SKILL 代码 |
| `test_connection(timeout)` | 测试连接 |

## 兼容性别名

`SkillResult` 是 `VirtuosoResult` 的别名。
