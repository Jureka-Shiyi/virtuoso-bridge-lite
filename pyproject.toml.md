

# 一、整段配置的作用
这个文件告诉 Python：
1. 你的包叫什么
2. 版本多少
3. 依赖哪些库
4. 代码在哪里
5. 安装时要包含哪些资源文件
6. 提供什么命令行工具

---

# 二、逐段详细解释（超级易懂）

## 1. 构建系统（固定写法）
```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"
```
含义：
- **构建工具用 setuptools**（Python 官方标准打包工具）
- 要求版本 ≥64
- `build-backend` 是打包后台，固定写法

---

## 2. 项目基本信息
```toml
[project]
name = "virtuoso-bridge"
version = "0.1.0"
description = "Lightweight Python bridge for Cadence Virtuoso SKILL execution and Spectre simulation"
requires-python = ">=3.9"
```
含义：
- **包名**：`virtuoso-bridge`（别人 pip install 时用的名字）
- **版本**：0.1.0
- **描述**：轻量级 Python 桥接工具，用于 Cadence Virtuoso 的 SKILL 执行与 Spectre 仿真
- **要求 Python ≥3.9**

---

## 3. 运行依赖（必须安装）
```toml
dependencies = [
    "python-dotenv>=1.0",
    "pydantic>=2.0",
]
```
含义：
- 安装你的包时，**自动安装这两个库**
- `python-dotenv`：读取环境变量
- `pydantic`：数据验证（现代 Python 必备）

---

## 4. 命令行工具（最实用！）
```toml
[project.scripts]
virtuoso-bridge = "virtuoso_bridge.cli:main"
```
含义：
**安装后，你可以直接在终端敲：**
```bash
virtuoso-bridge
```
它会自动执行：
```
virtuoso_bridge/cli.py 里的 main() 函数
```
这就是**命令行工具的注册**。

---

## 5. 开发依赖（可选）
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7",
]
```
含义：
- 只在**开发/测试**时需要
- 安装方式：
```bash
pip install -e ".[dev]"
```
会自动装 pytest 测试工具

---

## 6. 代码在哪里（非常重要）
```toml
[tool.setuptools.packages.find]
where = ["src"]
```
含义：
- **你的代码全部放在 src/ 文件夹下**
- pip 会自动从 `src/` 里找包
- 你的目录结构一定是：
```
src/
   virtuoso_bridge/
       __init__.py
       ...
```

---

## 7. 打包时包含的资源文件
```toml
[tool.setuptools.package-data]
"virtuoso_bridge.resources" = [".env_template"]
"virtuoso_bridge.virtuoso.basic.resources" = ["*.il", "*.py"]
```
含义：
安装包时，**自动把这些文件一起打包**：
1. `.env_template` 环境变量模板
2. 所有 `.il` 文件（SKILL 脚本）
3. 所有 `.py` 辅助脚本

这就是你之前看到的 `ramic_bridge.il` 等文件能被包找到的原因！

---

# 三、一句话总结整个文件
> **这是 Python 包的“身份证+安装说明书”**
> 告诉 pip 你的包叫什么、依赖什么、代码在哪、带什么脚本、提供什么命令。

---

# 四、和你之前的代码关系（重点）
你之前的：
- `ramic_bridge.il`
- `ramic_daemon.py`
- `bridge_client.py`

就是通过 **package-data** 被包含进包里的，所以安装后可以直接被 Python 调用，不用手动复制文件。

---
