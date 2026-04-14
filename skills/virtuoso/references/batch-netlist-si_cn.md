# 批量网表（si）

在不使用 Maestro 的情况下生成 Spectre/HSPICE 网表，使用 `si` 批量翻译器。适用于自动化和 CI 流水线。

## 从 CIW 生成 si.env

不要手动编写 `si.env`——让 Virtuoso 生成它：

```python
# 在远程生成 si.env
client.execute_skill('sh("mkdir -p /tmp/si_run")')
client.execute_skill(
    'simInitEnvWithArgs("/tmp/si_run" "myLib" "myCell" "schematic" "spectre" nil)')

# 下载以检查或修改
client.download_file("/tmp/si_run/si.env", "output/si.env")
```

`simInitEnvWithArgs(runDir libName cellName viewName simulator nil)`——最后一个参数未使用，传递 nil。

## si.env 字段

| 字段 | 含义 | 示例 |
|------|------|------|
| `simLibName` | 库名 | `"2025_FIA"` |
| `simCellName` | 单元名 | `"_TB_INPUT_BUFFER_CASCODE_PSS"` |
| `simViewName` | 视图 | `"schematic"` |
| `simSimulator` | 仿真器类型 | `"spectre"` 或 `"hspice"` |
| `simViewList` | 网表生成的视图搜索顺序 | `'("spectre cmos_sch schematic veriloga")` |
| `simStopList` | 在这些视图处停止下降 | `'("spectre")` |
| `simNetlistHier` | 分层网表 | `t` |
| `nlDesignVarNameList` | 要包含的设计变量 | `'("VDD" "CL" "f")` |

## 运行 si 批量网表

```python
# 通过 bridge 在远程运行 si（csh 语法——使用 ; 而不是 &&）
client.run_shell_command(
    'mkdir -p /tmp/si_run ; '
    'cp /path/to/si.env /tmp/si_run/ ; '
    'cd /tmp/si_run ; '
    'si -batch -cdslib /home/zhangz/tsmc28/RISCA/cds.lib -command nl')

# 下载网表
client.download_file("/tmp/si_run/netlist", "output/si_netlist.scs")
```

- 对于 Spectre：使用 `-command nl`（不是 `netlist`——那会导致 OSSHNL-510 错误）
- 对于 HSPICE/auCdl/Verilog：使用 `-command netlist`
- 如果 `cds.lib` 存在于主目录中，则可以省略 `-cdslib`
- `cds.lib` 路径可以通过：`client.execute_skill('simplifyFilename("./cds.lib")')` 找到
- `run_shell_command` 使用 csh——返回 `t`/`nil`，不是 stdout。不要依赖输出。

输出文件：`<runDir>/netlist`（单个文件，不是目录）。

## si vs Maestro 网表

| | si 网表 | Maestro 网表（`maeCreateNetlistForCorner`） |
|---|---|---|
| **电路结构** | 是 | 是（相同） |
| **parameters 行** | 否（变量保持符号） | 是（解析为值） |
| **模型 include** | 否 | 是 |
| **仿真命令** | 否 | 是（analysis、options） |
| **需要 Maestro** | 否 | 是（打开会话） |

si 给出纯电路网表。Maestro 给出可直接运行的仿真 deck。

## 在 Virtuoso GUI 中查看网表

```scheme
view("/tmp/si_run/netlist")
```

## 从 Maestro（替代方法）

如果 Maestro 会话已打开，`maeCreateNetlistForCorner` 更简单：

```scheme
maeCreateNetlistForCorner("IB_PSS" "Nominal" "/tmp/netlist_dir")
; 输出：/tmp/netlist_dir/netlist/input.scs

; 在 GUI 中查看
view("/tmp/netlist_dir/netlist/input.scs")
```
