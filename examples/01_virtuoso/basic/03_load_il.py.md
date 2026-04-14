# 加载 SKILL .il 文件到 Virtuoso

## 功能概述

本示例演示如何使用 `client.load_il()` 方法将本地 SKILL (.il) 文件加载到远程 Virtuoso CIW 中。

与 `02_ciw_print.py` 的对比：后者通过多次网络往返逐行打印，本方法则一次上传整个文件到远程执行。

## 核心方法

### `VirtuosoClient.load_il()`

```python
result = client.load_il(Path("path/to/script.il"))
```

**工作流程**：
1. 计算本地文件的 MD5 哈希
2. 检查缓存（相同哈希不会重复上传）
3. 上传文件到远程临时目录
4. 在 Virtuoso 中执行 `load()` 加载 IL 文件
5. 返回执行结果和元数据

### 返回值分析

```python
result.execution_time    # 执行耗时
result.status.value      # "success" 或 "error"
result.metadata.get("uploaded")  # True=新上传, None=缓存命中
result.metadata.get("skill_command")  # 实际执行的 SKILL 命令
```

## IL 文件上传缓存机制

`load_il()` 会缓存已上传的文件：
- **首次上传**：显示 `uploaded`
- **后续使用**：显示 `cache hit`，不重复上传

这对于频繁调用的 SKILL 辅助脚本非常高效。

## 使用示例

```python
from virtuoso_bridge import VirtuosoClient
from pathlib import Path

client = VirtuosoClient.from_env()

# 加载 SKILL 文件
IL_FILE = Path(__file__).parent.parent / "assets" / "sonnet18.il"
result = client.load_il(IL_FILE)

# 检查结果
print_elapsed("load_il", result.execution_time)
upload_tag = "uploaded" if result.metadata.get("uploaded") else "cache hit"
print(f"[{upload_tag}]")
```

## 适用场景

1. **加载复杂 SKILL 过程**：包含多行定义、函数库
2. **预置的辅助脚本**：如 `harvest_library.il`、`screenshot.il`
3. **批量操作**：需要多次使用的 SKILL 代码封装

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- 要加载的 .il 文件存在于本地

## 相关文件

本示例使用的 assets 文件：
- `assets/sonnet18.il` - 包含打印十四行诗的 SKILL 代码
