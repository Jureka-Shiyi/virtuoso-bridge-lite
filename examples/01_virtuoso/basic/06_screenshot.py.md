# 截图 Virtuoso 当前窗口

## 功能概述

本脚本捕获当前打开的 Virtuoso 窗口（layout 或 schematic）的截图，并保存到本地。

## 工作流程

```
1. 获取当前设计信息 (lib/cell/view)
2. 加载 screenshot.il 辅助脚本
3. 在远程创建截图目录
4. 执行 takeScreenshot() SKILL 命令
5. 下载截图到本地
```

## 代码逻辑解析

### 1. 获取当前设计

```python
elapsed, design = timed_call(client.get_current_design)
lib, cell, view = design
```

### 2. 加载截图辅助 IL

```python
IL_FILE = Path(__file__).resolve().parent.parent / "assets" / "screenshot.il"
load_result = client.load_il(IL_FILE)
```

### 3. 创建远程目录

```python
screenshot_dir = default_virtuoso_bridge_dir(username, "screenshots")
client._tunnel._ssh_runner.run_command(f"mkdir -p {screenshot_dir}")
```

使用 SSH 而非 SKILL csh 创建目录，因为 SSH 可访问的文件系统更可靠。

### 4. 执行截图

```python
result = client.execute_skill(
    f'takeScreenshot("{escape_skill_string(remote_path)}")',
    timeout=20
)
```

### 5. 下载到本地

```python
local_path = OUTPUT_DIR / Path(remote_path).name
client.download_file(remote_path, local_path, timeout=30)
```

## 输出文件

截图保存到：
```
examples/01_virtuoso/basic/output/<cell_name>_<timestamp>.png
```

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso 中有打开的 cellview
- `assets/screenshot.il` 存在

## 依赖

- `screenshot.il` - 包含 `takeScreenshot()` 函数
- SSH 文件系统访问权限

## 适用场景

- 自动化测试中记录设计状态
- 调试时保存设计快照
- 生成设计文档的插图
