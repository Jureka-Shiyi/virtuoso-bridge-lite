# helloWorld.il

## 功能概述

在 Virtuoso CIW 中打印欢迎信息和系统环境信息。

## 打印内容

运行此脚本会在 CIW 窗口中显示：

```
==================================================
[Current Date & Time] 2026-04-14 10:30:00
[Cadence Version] IC6.1.8-64b
[SKILL Version] 2020.12
[Current Path] /home/user/cadence
[Host Name] virtuoso-server
==================================================
Hello, World!
Welcome to your work session! Today is full of possibilities!
May your thinking be as clear as code and your creativity flow like circuits.
Whatever challenges you face, trust that your talent will find the optimal solution!
Work efficiently, create freely, and make today extraordinary!
==================================================
```

## 代码解析

### 环境信息获取函数

| 函数 | 返回内容 |
|------|---------|
| `getCurrentTime()` | 当前日期和时间 |
| `getVersion()` | Cadence 版本 |
| `getSkillVersion()` | SKILL 版本 |
| `getWorkingDir()` | 当前工作目录 |
| `getHostName()` | 主机名 |

## 使用方法

### 通过 Python 调用

```python
client = VirtuosoClient.from_env()
result = client.load_il(Path("path/to/helloWorld.il"))
```

### 直接在 Virtuoso CIW 中加载

```skill
load("path/to/helloWorld.il")
```

## 用途

- 验证 virtuoso-bridge 连接是否正常
- 检查 CIW 输出是否工作正常
- 作为测试占位符脚本
