# virtuoso_bridge

## 功能概述

Python bridge for executing SKILL in Cadence Virtuoso. 提供 Virtuoso SKILL 执行、SSH 隧道管理、 Spectre 仿真运行的功能。

## 主要导出

| 导出 | 类型 | 说明 |
|------|------|------|
| `VirtuosoClient` | 类 | Virtuoso SKILL 执行客户端 |
| `SSHClient` | 类 | SSH 隧道和远程文件部署管理 |
| `SpectreSimulator` | 类 | Cadence Spectre 仿真器适配器 |
| `VirtuosoResult` | 类 | SKILL 执行结果数据模型 |
| `ExecutionStatus` | 枚举 | 执行状态枚举 |
| `SimulationResult` | 类 | 仿真结果数据模型 |
| `SkillResult` | 类 | VirtuosoResult 的兼容性别名 |
| `decode_skill_output()` | 函数 | 解码原始 SKILL 输出 |

## 使用示例

```python
from virtuoso_bridge import VirtuosoClient, decode_skill_output

# 从环境变量创建客户端
client = VirtuosoClient.from_env()

# 执行 SKILL 代码
result = client.execute_skill("1+2")
print(result.output)  # "3"

# 解码 SKILL 输出
decoded = decode_skill_output('"hello\\nworld"')
```

## 协议

- **SKILL 桥接协议**: 通过 TCP 与 Virtuoso CIW 中的 RAMIC 守护进程通信
- **请求格式**: `{"skill": "...", "timeout": 30}`
- **响应格式**: `\x02<result>\x1e` (成功) 或 `\x15<error>\x1e` (失败)

## 相关模块

- `virtuoso_bridge.transport` - SSH 传输层
- `virtuoso_bridge.virtuoso` - Virtuoso 客户端封装
- `virtuoso_bridge.spectre` - Spectre 仿真器封装
