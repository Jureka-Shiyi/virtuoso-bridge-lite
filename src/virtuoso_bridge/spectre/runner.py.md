# SpectreSimulator

## 功能概述

Cadence Spectre 仿真器适配器，支持本地和远程仿真，上传网表、运行仿真、下载和解析 PSF 结果。

## SpectreSimulator 类

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `spectre_cmd` | `str` | `"spectre"` | Spectre 命令 |
| `spectre_args` | `list \| tuple` | `None` | Spectre 额外参数 |
| `timeout` | `int` | `600` | 超时时间（秒） |
| `work_dir` | `Path \| None` | `None` | 工作目录 |
| `output_format` | `str \| None` | `"psfascii"` | 输出格式 |
| `remote_host` | `str \| None` | `None` | 远程主机 |
| `remote_user` | `str \| None` | `None` | 远程用户 |
| `remote_work_dir` | `str \| None` | `None` | 远程工作目录 |
| `jump_host` | `str \| None` | `None` | 跳板机 |
| `keep_remote_files` | `bool` | `False` | 保留远程文件 |
| `profile` | `str \| None` | `None` | 配置profile |

### 工厂方法

| 方法 | 说明 |
|------|------|
| `from_env(profile)` | 从环境变量创建 |
| `local(spectre_cmd, timeout, work_dir)` | 创建本地仿真器 |

### 核心方法

| 方法 | 说明 |
|------|------|
| `run_simulation(netlist, params)` | 运行单次仿真 |
| `submit(netlist, params)` | 提交后台仿真任务（返回 Future） |
| `run_parallel(tasks, max_workers)` | 并行运行多个仿真 |
| `wait_all(futures)` | 等待所有 Future 完成 |
| `set_max_workers(n)` | 设置最大并发数 |
| `shutdown()` | 关闭工作线程池 |
| `check_license()` | 检查许可证可用性 |

### 使用示例

```python
from virtuoso_bridge.spectre.runner import SpectreSimulator, spectre_mode_args
from pathlib import Path

# 创建仿真器
sim = SpectreSimulator.from_env(
    spectre_args=spectre_mode_args("ax"),  # APS 扩展模式
    work_dir="./output",
)

# 单次运行
result = sim.run_simulation(Path("my_netlist.scs"), {})
if result.ok:
    vout = result.data["VOUT"]

# 并行提交
t1 = sim.submit(Path("tb1.scs"), {})
t2 = sim.submit(Path("tb2.scs"), {"include_files": ["model.va"]})
results = SpectreSimulator.wait_all([t1, t2])
```

## 仿真模式参数

```python
spectre_mode_args("spectre")  # 基本模式
spectre_mode_args("aps")      # APS 模式
spectre_mode_args("ax")       # APS 扩展模式（推荐）
spectre_mode_args("cx")       # Spectre X 自定义
```

## 任务管理

| 函数 | 说明 |
|------|------|
| `read_all_jobs()` | 读取所有任务记录 |
| `cancel_job(job_id)` | 取消指定任务 |

任务状态保存在 `~/.cache/virtuoso_bridge/jobs/` 目录。
