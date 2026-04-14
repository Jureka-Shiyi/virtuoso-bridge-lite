# Hello World - 执行 SKILL 表达式

## 功能概述

这是最基本的示例，展示如何：
1. 通过 `execute_skill()` 执行简单的 SKILL 表达式
2. 获取系统信息（日期、版本、工作目录等）
3. 执行基本运算和字符串操作

## 执行流程

```
Python Client → SSH Tunnel → Virtuoso → 返回结果 → Python
```

## 代码逻辑解析

### 1. 打印横幅到 CIW

```python
skill_cmd = r'printf("\n\n==============================================\nHello, Virtuoso!\n==============================================\n")'
r = client.execute_skill(skill_cmd)
```

使用原始字符串（`r''`）避免转义字符问题。

### 2. 获取系统信息

| 信息类型 | SKILL 代码 | 返回值示例 |
|---------|-----------|-----------|
| 日期时间 | `getCurrentTime()` | `Tue Apr 14 10:30:00 2026` |
| Cadence 版本 | `getVersion()` | `IC6.1.8-64b` |
| SKILL 版本 | `getSkillVersion()` | `2020.12` |
| 工作目录 | `getWorkingDir()` | `/home/user/cadence` |
| 主机名 | `getHostName()` | `virtuoso-server` |

### 3. 基础运算

```python
# 算术运算
skill_cmd = r'let((v) v=1+2 printf("[Arithmetic]      1+2 = %d\n" v) v)'
# 返回: 3

# 字符串拼接
skill_cmd = r'let((v) v=strcat("Hello" " from SKILL") printf("[String]          %s\n" v) v)'
# 返回: Hello from SKILL
```

## 常用 SKILL 函数速查

| 函数 | 作用 | 示例 |
|------|------|------|
| `printf()` | 打印到 CIW | `printf("Value: %d\n" x)` |
| `getCurrentTime()` | 获取当前时间 | 返回时间字符串 |
| `getVersion()` | 获取 Cadence 版本 | 返回版本号 |
| `getSkillVersion()` | 获取 SKILL 版本 | 返回版本号 |
| `getWorkingDir()` | 获取工作目录 | 返回路径字符串 |
| `getHostName()` | 获取主机名 | 返回主机名 |
| `strcat()` | 字符串拼接 | `strcat("a" "b")` → `"ab"` |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW

## 扩展应用

本示例是后续所有高级功能的基础。掌握这些基本操作后，你可以：

- 读取设计数据库信息
- 执行自定义 SKILL 脚本
- 与 Virtuoso 进行复杂的数据交互
