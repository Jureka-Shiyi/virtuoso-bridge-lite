# virtuoso-bridge-lite 项目结构文档

本文档详细描述了 `virtuoso-bridge-lite` 项目的目录结构和各文件夹内容。

---

## 根目录 (`/`)

项目根目录包含主要的配置文件和文档。

| 文件 | 描述 |
|------|------|
| `README.md` | 项目主页文档，包含项目介绍、快速开始、架构说明 |
| `AGENTS.md` | AI Agent 专用指南，详细说明设置步骤和关键约定 |
| `pyproject.toml` | Python 包配置文件，定义依赖、脚本入口等 |
| `.gitignore` | Git 忽略规则 |
| `PROJECT_STRUCTURE.md` | 本文件，项目结构说明 |

---

## `core/` - 核心机制（精简版）

整个桥接机制的精简实现，仅用 3 个文件（约 180 行代码）展示核心原理。

| 文件 | 描述 |
|------|------|
| `README.md` | 核心架构说明和使用指南 |
| `ramic_bridge.il` | SKILL 端 IPC 代码，在 Virtuoso CIW 中加载 |
| `ramic_daemon.py` | TCP 到 Virtuoso 的 IPC 中继守护进程 |
| `bridge_client.py` | 最小化 Python 客户端，演示 SKILL 执行 |

**用途**：理解底层机制，无需 pip 安装即可使用。

---

## `src/virtuoso_bridge/` - 完整 Python 包

生产级 Python 包，提供完整的远程 Virtuoso 控制能力。

### `src/virtuoso_bridge/`（根包）

| 文件 | 描述 |
|------|------|
| `__init__.py` | 包初始化，导出主要类（VirtuosoClient 等） |
| `cli.py` | CLI 实现：`virtuoso-bridge start/status/restart` |
| `models.py` | 数据模型定义（结果类型、配置类等） |

### `src/virtuoso_bridge/resources/`

| 文件 | 描述 |
|------|------|
| `__init__.py` | 资源包初始化 |
| `x11_dismiss_dialog.py` | X11 对话框自动关闭工具 |
| `.env_template` | 环境变量模板（打包时包含） |

### `src/virtuoso_bridge/transport/` - 传输层

| 文件 | 描述 |
|------|------|
| `__init__.py` | 传输包初始化 |
| `ssh.py` | SSH 客户端实现，管理连接和命令执行 |
| `tunnel.py` | SSH 隧道管理，端口转发 |
| `remote_paths.py` | 远程路径处理工具 |

### `src/virtuoso_bridge/virtuoso/` - Virtuoso 控制

#### `virtuoso/basic/` - 基础桥接

| 文件 | 描述 |
|------|------|
| `__init__.py` | 基础包初始化 |
| `bridge.py` | VirtuosoClient 主类实现 |
| `composition.py` | 组合操作工具 |
| `resources/` | 守护进程资源文件 |
| `resources/ramic_bridge_daemon_3.py` | Python 3 守护进程 |
| `resources/ramic_bridge_daemon_27.py` | Python 2.7 守护进程 |

#### `virtuoso/layout/` - 版图编辑

| 文件 | 描述 |
|------|------|
| `__init__.py` | 导出 LayoutEditor 和相关操作 |
| `editor.py` | LayoutEditor 类，版图编辑上下文管理器 |
| `ops.py` | 版图操作：创建矩形、路径、通孔、实例等 |
| `reader.py` | 版图读取功能 |

#### `virtuoso/schematic/` - 原理图编辑

| 文件 | 描述 |
|------|------|
| `__init__.py` | 导出 SchematicEditor 和相关操作 |
| `editor.py` | SchematicEditor 类，原理图编辑上下文管理器 |
| `ops.py` | 原理图操作：添加实例、连线、引脚等 |
| `reader.py` | 原理图读取和连接关系分析 |
| `params.py` | CDF 参数设置工具 |

#### `virtuoso/maestro/` - Maestro 仿真配置

| 文件 | 描述 |
|------|------|
| `__init__.py` | 导出 Maestro 相关功能 |
| `session.py` | Maestro 会话管理（打开/关闭） |
| `reader.py` | 读取 Maestro 配置（测试、分析、变量） |
| `writer.py` | 修改 Maestro 配置 |

#### `virtuoso/ops.py`
通用 Virtuoso 操作（截图、文件操作等）。

#### `virtuoso/x11.py`
X11 相关操作（窗口管理等）。

### `src/virtuoso_bridge/spectre/` - Spectre 仿真

| 文件 | 描述 |
|------|------|
| `__init__.py` | 导出 SpectreSimulator |
| `runner.py` | SpectreSimulator 类，运行仿真 |
| `parsers.py` | PSF 结果文件解析器 |

---

## `skills/` - AI Agent 技能文档

为 AI Agent（如 Claude Code）提供的技能文件，让 Agent 知道如何使用本工具。

### `skills/virtuoso/` - Virtuoso 技能

| 文件 | 描述 |
|------|------|
| `SKILL.md` | Virtuoso 技能主文档，包含完整使用指南 |
| `references/schematic-python-api.md` | 原理图 Python API 参考 |
| `references/schematic-skill-api.md` | 原理图 SKILL API 参考 |
| `references/layout-python-api.md` | 版图 Python API 参考 |
| `references/layout-skill-api.md` | 版图 SKILL API 参考 |
| `references/maestro-python-api.md` | Maestro Python API 参考 |
| `references/maestro-skill-api.md` | Maestro SKILL API 参考 |
| `references/netlist.md` | 网表格式说明（CDL/Spectre） |
| `references/batch-netlist-si.md` | 批处理网表生成（si 命令） |
| `references/schematic-recreation.md` | 从现有设计重建原理图指南 |
| `references/testbench-migration.md` | 测试平台迁移指南 |
| `references/troubleshooting.md` | 常见问题排查 |
| `references/netlist_samples/` | 网表示例文件 |

### `skills/spectre/` - Spectre 技能

| 文件 | 描述 |
|------|------|
| `SKILL.md` | Spectre 仿真技能主文档 |
| `references/netlist_syntax.md` | Spectre 网表语法参考 |
| `references/parallel.md` | 并行仿真和多服务器配置 |

### `skills/optimizer/` - 优化器技能

| 文件 | 描述 |
|------|------|
| `SKILL.md` | 电路优化相关技能 |

---

## `examples/` - 示例代码

### `examples/01_virtuoso/` - Virtuoso 示例

#### `01_virtuoso/basic/` - 基础操作示例

| 文件 | 描述 |
|------|------|
| `00_ciw_output_vs_return.py` | CIW 输出 vs Python 返回值对比 |
| `01_execute_skill.py` | 执行 SKILL 表达式基础示例 |
| `02_ciw_print.py` | 向 CIW 打印多行消息 |
| `03_load_il.py` | 上传并加载 .il 文件 |
| `04_list_library_cells.py` | 列出库和单元 |
| `05_multiline_skill.py` | 多行 SKILL 代码执行 |
| `05_harvest_library.py` | 库单元收集 |
| `06_screenshot.py` | 截图功能示例 |

#### `01_virtuoso/schematic/` - 原理图编辑示例

| 文件 | 描述 |
|------|------|
| `01a_create_rc_stepwise.py` | 分步创建 RC 原理图 |
| `01b_create_rc_load_skill.py` | 通过 .il 脚本创建 RC 原理图 |
| `02_read_connectivity.py` | 读取连接关系 |
| `03_read_instance_params.py` | 读取实例参数 |
| `05_rename_instance.py` | 重命名实例 |
| `06_delete_instance.py` | 删除实例 |
| `07_delete_cell.py` | 删除单元 |
| `08_import_cdl_cap_array.py` | 通过 spiceIn 导入 CDL |

#### `01_virtuoso/layout/` - 版图编辑示例

| 文件 | 描述 |
|------|------|
| `01_create_layout.py` | 创建版图（矩形、路径、实例） |
| `02_add_polygon.py` | 添加多边形 |
| `03_add_via.py` | 添加通孔 |
| `04_multilayer_routing.py` | 多层布线 |
| `05_bus_routing.py` | 总线布线 |
| `06_read_layout.py` | 读取版图形状 |
| `07_delete_shapes_on_layer.py` | 删除指定层上的形状 |
| `08_clear_routing.py` | 清除布线 |
| `09_clear_current_layout.py` | 清除当前版图 |
| `10_delete_cell.py` | 删除单元 |
| `flower.py` | 版图艺术示例（花朵图案） |

#### `01_virtuoso/maestro/` - Maestro 仿真示例

| 文件 | 描述 |
|------|------|
| `01_read_open_maestro.py` | 读取当前打开的 Maestro |
| `02_gui_open_read_close_maestro.py` | GUI 模式打开-读取-关闭 |
| `03_bg_open_read_close_maestro.py` | 后台模式打开-读取-关闭 |
| `04_read_env.py` | 读取环境设置 |
| `05_read_results.py` | 读取仿真结果 |
| `06a_rc_create.py` | 创建 RC 原理图 + Maestro 设置 |
| `06b_rc_simulate_and_read.py` | 运行仿真并读取结果 |

#### `01_virtuoso/assets/` - 示例资源文件

| 文件 | 描述 |
|------|------|
| `file_ops.il` | 文件操作 SKILL 脚本 |
| `harvest_library.il` | 库收集 SKILL 脚本 |
| `helloWorld.il` | Hello World SKILL 示例 |
| `layout_ops.il` | 版图操作 SKILL 脚本 |
| `maestro_utils.il` | Maestro 工具脚本 |
| `screenshot.il` | 截图 SKILL 脚本 |
| `sonnet18.il` | 文学示例（莎士比亚十四行诗） |

### `examples/02_spectre/` - Spectre 仿真示例

| 文件 | 描述 |
|------|------|
| `01_inverter_tran.py` | 反相器瞬态仿真 |
| `01_veriloga_adc_dac.py` | Verilog-A ADC/DAC 仿真 |
| `02_cap_dc_ac.py` | 电容 DC+AC 仿真 |
| `04_strongarm_pss_pnoise.py` | StrongArm 比较器 PSS+Pnoise 仿真 |
| `_result_io.py` | 结果 I/O 辅助工具 |

#### `02_spectre/assets/` - 仿真资源

| 子目录 | 描述 |
|--------|------|
| `adc_dac_ideal_4b/` | 4 位理想 ADC/DAC 示例 |
| `cap_dc_ac/` | 电容仿真示例 |
| `inv_tb/` | 反相器测试平台 |
| `strongarm_cmp/` | StrongArm 比较器示例 |

---

## `assets/` - 文档资源

| 文件 | 描述 |
|------|------|
| `banner.svg` | 项目横幅 SVG 图像 |
| `arch.png` | 架构图 PNG 图像 |
| `.DS_Store` | macOS 系统文件（可忽略） |

---

## `scripts/` - 脚本工具

| 文件 | 描述 |
|------|------|
| `fix-symlinks.sh` | Windows 符号链接修复脚本（解决 Git 克隆问题） |

---

## `.claude/skills/` - Claude Code 技能链接

Claude Code 技能目录的符号链接，指向 `skills/` 目录。

| 文件 | 链接目标 | 描述 |
|------|----------|------|
| `virtuoso` | `../../skills/virtuoso` | Virtuoso 技能入口 |
| `spectre` | `../../skills/spectre` | Spectre 技能入口 |
| `optimizer` | `../../skills/optimizer` | 优化器技能入口 |

---

## `docs/` - 文档网站

| 文件 | 描述 |
|------|------|
| `index.html` | 文档网站首页 |
| `favicon.svg` | 网站图标 |
| `CNAME` | 自定义域名配置 |
| `superpowers/plans/` | 功能规划文档 |

---

## 文件数量统计

| 目录 | 文件数（约） | 类型 |
|------|-------------|------|
| `core/` | 4 | SKILL + Python |
| `src/` | 25+ | Python 包 |
| `skills/` | 15+ | Markdown 文档 |
| `examples/` | 40+ | Python + SKILL |
| `scripts/` | 1 | Shell 脚本 |
| `assets/` | 2 | 图像 |
| `docs/` | 3+ | HTML/配置 |

---

## 使用建议

1. **新手入门**：先阅读 `AGENTS.md`，然后从 `examples/01_virtuoso/basic/` 开始
2. **理解原理**：查看 `core/` 目录的精简实现
3. **开发使用**：使用完整包 `src/virtuoso_bridge/`
4. **AI Agent**：参考 `skills/` 目录下的技能文档
5. **遇到问题**：查看 `skills/virtuoso/references/troubleshooting.md`

---

*本文档由 AI 自动生成，更新时间：2026-04-11*
