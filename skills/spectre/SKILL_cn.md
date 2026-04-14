---
name: spectre
description: "通过 virtuoso-bridge 远程运行 Cadence Spectre 仿真：通过 SSH 上传网表、执行仿真、解析 PSF 结果。当用户想要从网表文件运行 SPICE/Spectre 仿真、在 Virtuoso GUI 外部进行 transient/AC/PSS/pnoise 分析、解析 PSF 波形数据、在单机或多服务器上并行运行多个仿真、检查仿真任务状态、或提到 Spectre APS/AXS 模式时，触发此技能。同时也适用于 sim-jobs、sim-cancel 或并行/并发仿真请求。此技能用于独立的网表驱动仿真——对于基于 GUI 的 ADE Maestro 仿真，请使用 virtuoso 技能。"
---

# Spectre 技能

上传 `.scs` 网表到远程机器，通过 SSH 运行 Spectre，下载并解析 PSF 结果为 Python 字典。独立于 VirtuosoClient——无需 GUI。

## 开始之前

1. **`virtuoso-bridge` 是一个 Python CLI**——通过 `pip install -e virtuoso-bridge-lite` 安装。
2. `virtuoso-bridge status`——检查连接、Spectre 路径、许可证
3. 查看 `examples/02_spectre/`——以现有示例为基础
4. `.env` 必须设置 `VB_CADENCE_CSHRC`（可以放在项目根目录或 virtuoso-bridge-lite 目录中）

## 核心模式

```python
from virtuoso_bridge.spectre.runner import SpectreSimulator, spectre_mode_args

sim = SpectreSimulator.from_env(
    spectre_args=spectre_mode_args("ax"),  # APS 扩展模式（推荐）
    work_dir="./output",
)
result = sim.run_simulation("my_netlist.scs", {})

if result.ok:
    vout = result.data["VOUT"]
else:
    print(result.errors)
```

包含 Verilog-A include 文件：
```python
result = sim.run_simulation("tb_adc.scs", {"include_files": ["adc.va", "dac.va"]})
```

## 结果对象

| 属性 | 内容 |
|------|------|
| `result.ok` | 仿真是否成功 |
| `result.data` | `{"signal_name": [float, ...]}` 解析后的波形数据 |
| `result.errors` | 错误消息（简短、分类） |
| `result.metadata["timings"]` | 上传、执行、下载、解析耗时 |
| `result.metadata["output_dir"]` | `.raw` 目录的本地路径 |

## 并行仿真

提交并发运行的仿真——每个仿真使用独立的远程目录，无冲突。有关完整 API 和多服务器设置，请阅读 `references/parallel.md`。

```python
t1 = sim.submit(Path("tb_comp.scs"))    # 立即返回 Future
t2 = sim.submit(Path("tb_dac.scs"))     # 随时提交更多
result = t1.result()                     # 阻塞等待一个
results = SpectreSimulator.wait_all([t1, t2])  # 或等待整个批次
```

CLI 监控：`virtuoso-bridge sim-jobs`（显示 user@host、CPU/MEM、时间）和 `virtuoso-bridge sim-cancel <id>`。

## 仿真模式

```python
spectre_mode_args("spectre")  # 基本模式（许可证需求最少）
spectre_mode_args("aps")      # APS 模式
spectre_mode_args("ax")       # APS 扩展模式（推荐）
spectre_mode_args("cx")       # Spectre X 自定义模式
```

## 参考文档

需要时加载——这些包含详细的 API 文档：

- `references/netlist_syntax.md`——Spectre 网表格式、分析语句、参数化
- `references/parallel.md`——并行仿真、多服务器、CLI 任务管理、.env 配置

## 示例

- `examples/02_spectre/01_inverter_tran.py`——反相器瞬态仿真
- `examples/02_spectre/01_veriloga_adc_dac.py`——4 位 ADC/DAC 含 Verilog-A
- `examples/02_spectre/02_cap_dc_ac.py`——电容 DC + AC 分析
- `examples/02_spectre/04_strongarm_pss_pnoise.py`——StrongArm PSS + Pnoise 分析

## 相关技能

- **virtuoso**——基于 GUI 的 Virtuoso 工作流程（schematic/layout、ADE Maestro）。在 Virtuoso GUI 中工作时使用。
