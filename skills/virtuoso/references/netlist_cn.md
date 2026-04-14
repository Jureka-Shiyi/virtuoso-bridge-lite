# 网表参考

## 格式

### CDL（电路描述语言）

SPICE 兼容格式，用于 LVS 验证和原理图导入。

```
.SUBCKT cap_unit TOP BOT
C0 TOP BOT cap C=1e-14
.ENDS

.SUBCKT cap_array_4b TOP BOT<3:0>
XC_b0_0 TOP BOT<0> cap_unit
XC_b1_0 TOP BOT<1> cap_unit
.ENDS
```

语法：
- `.SUBCKT name pin1 pin2 ...` / `.ENDS`
- 实例：`name node1 node2 model [params]`
- 子电路实例：`Xname node1 node2 subcktName [params]`
- 总线表示法：`BOT<3:0>`、`BOT<0>`

### Spectre

Cadence Spectre 仿真器格式，用于仿真。

```
subckt cap_unit (TOP BOT)
    C0 (TOP BOT) capacitor c=1e-14
ends cap_unit

XC_b0_0 (TOP BOT\<0\>) cap_unit
```

语法：
- `subckt name (pin1 pin2)` / `ends name`
- 实例：`name (node1 node2) model param=value`
- 总线表示法：`BOT\<0\>`（用反斜杠转义尖括号）
- 器件名称是全名：`capacitor`、`resistor`、`inductor`（不是 `cap`、`res`、`ind`）

### 关键区别

| | CDL | Spectre |
|--|-----|---------|
| 用途 | LVS、原理图导入 | 仿真 |
| 引脚语法 | `TOP BOT` | `(TOP BOT)` |
| 器件名称 | 短：`cap`、`res`、`ind` | 全名：`capacitor`、`resistor`、`inductor` |
| 总线转义 | `BOT<0>` | `BOT\<0\>` |
| 子电路结束 | `.ENDS` | `ends name` |
| 参数 | `C=1e-14` | `c=1e-14` |
| 大小写 | 关键字大多大写 | 小写 |

## 参数名称映射

某些参数在原理图 CDF 和网表中有不同名称：

| 原理图 CDF | Spectre/CDL 网表 | 描述 |
|------------|--------------------|------|
| `acm` | `mag` | AC 幅值 |
| `vdc` | `dc` | DC 电压 |
| `r` | `r` | 电阻（相同） |
| `c` | `c` | 电容（相同） |

## 源器件映射

原理图中的 `analogLib/vsin` 在 Spectre 网表中变为 `vsource type=sine`。Spectre 中没有单独的 `vsin` 器件——它是 `vsource` 的一种模式。

`spiceIn` 导入含 `vsin` 的 CDL 会创建 `analogLib/vsource`（不是 `analogLib/vsin`）。要在原理图中获得 `vsin`，可以：
- 导入后手动更改实例 master
- 使用 `client.schematic.edit()` 添加具有正确 master 的源
- 通过 SKILL 添加源：`dbCreateInst(cv dbOpenCellView("analogLib" "vsin" "symbol") ...)`

## 导入：CDL → Virtuoso 原理图

使用 `spiceIn`（Cadence 命令行工具）。必须通过 SSH 运行，不能通过 SKILL `system()`。

```bash
spiceIn -language SPICE \
  -netlistFile input.cdl \
  -outputLib PLAYGROUND_LLM \
  -reflibList "analogLib basic" \
  -devmapFile devmap.txt
```

器件映射文件（`devmap.txt`）：
```
devselect := resistor res
devselect := capacitor cap
devselect := inductor ind
```

**spiceIn 导入后的符号生成：**
```python
# 重要：必须是单行 SKILL 字符串——多行 f-string 带换行符会导致通过 bridge 的 SKILL 解析失败
client.execute_skill(f'schPinListToSymbol("{lib}" "{cell}" "symbol" schSchemToPinList("{lib}" "{cell}" "schematic"))')
```
该函数适用于所有单元。永远不要手动创建符号。用 `ddGetObj(lib cell)~>views~>name` 验证。

关键点：
- **自动布线**——实例、net、引脚全部自动连接
- **自动生成子电路符号**（如果参考库有）
- **必须通过 SSH 运行**——`spiceIn` 启动内部 Virtuoso 进程，从 SKILL `system()` 调用会死锁 CIW
- 单元名称来自 CDL 中的 `.SUBCKT` 名称
- `spiceIn` 路径：`{cdsGetInstPath()}/bin/spiceIn`
- 需要 Cadence 环境：`LM_LICENSE_FILE`、`IC_HOME`、`LD_LIBRARY_PATH`

## 导出：Virtuoso 原理图 → Spectre 网表

使用 `maeCreateNetlistForCorner`（需要临时 Maestro 视图）。

```python
# 创建临时 maestro
ses = client.execute_skill(f'maeOpenSetup("{lib}" "{cell}" "maestro")').output.strip('"')
client.execute_skill(f'maeCreateTest("T1" ?lib "{lib}" ?cell "{cell}" ?view "schematic" ?simulator "spectre" ?session "{ses}")')
client.execute_skill(f'maeSaveSetup(?lib "{lib}" ?cell "{cell}" ?view "maestro" ?session "{ses}")')

# 导出
client.execute_skill(f'maeCreateNetlistForCorner("T1" "Nominal" "/tmp/netlist_dir")')

# 读取：/tmp/netlist_dir/netlist/input.scs
client.download_file('/tmp/netlist_dir/netlist/input.scs', 'output/netlist.scs')
```

关键点：
- 输出 Spectre 格式（不是 CDL）
- 完整正确——包含子电路层次结构、模型 include、仿真器选项
- 通过 `si -batch` 的 `auCdl` 导出在 Virtuoso 外部**不能可靠工作**（缺少 SKILL 回调）

## 直接原理图读取 → 网表

原理图数据库（实例、net、终端）可以直接通过 SKILL 读取，并组装成任何网表格式，不依赖外部网表生成器。参见 `examples/01_virtuoso/schematic/02_read_connectivity.py`。

关键 SKILL 访问器：
- `cv~>instances` → 所有实例
- `inst~>instTerms` → 实例终端
- `instTerm~>net~>name` → 连接的 net 名称
- `cv~>nets` → 所有 net
- `net~>instTerms` → net 上的所有 inst.term 对
- `cv~>terminals` → 顶层引脚和方向

这给出了与 CDL 或 Spectre 网表生成器相同的连接信息——只需格式化为目标语法。注意：
- 总线表示法：原理图中 `BOT<0>`，Spectre 中 `BOT\<0\>`
- 器件名称：`cap`（CDL）vs `capacitor`（Spectre）
- 引脚顺序：CDL 使用位置，Spectre 使用 `(node1 node2)`
- 参数：CDL `C=1e-14`，Spectre `c=1e-14`

## 往返：创建 → 导出 → 导入

```
Python API → Virtuoso 原理图
                ↓ maeCreateNetlistForCorner
           Spectre 网表
                ↓ 文本转换（Spectre → CDL）
              CDL 文件
                ↓ spiceIn（SSH）
           Virtuoso 原理图（新单元名称）
```

Spectre → CDL 转换是简单的文本处理：
- `subckt name (pins)` → `.SUBCKT name pins`
- `ends name` → `.ENDS`
- `(node1 node2) capacitor c=` → `node1 node2 cap C=`
- 移除总线括号上的反斜杠转义

## 示例网表

同一电路的三种表示：2 位 CDAC（cap_unit × [1,2]），带 1Ω 电阻从电容顶板到 VOUT。

```
        VOUT ──[R0 1Ω]── TOP ──┬── cap_unit (BOT<0>)  ← bit0, ×1
                                ├── cap_unit (BOT<1>)  ← bit1, ×2
                                └── cap_unit (BOT<1>)
```

`references/netlist_samples/` 中的示例文件——2 级 RC 低通级联（rc_unit → rc_cascade_2 → tb_rc_cascade，含 vsin 源）。从实际 CDL → spiceIn → Virtuoso → 导出流程生成，AC 验证（159 MHz 处 2 极点滚降）。

- `netlist_samples/rc_cascade.cdl`——CDL 输入（真实来源，喂给 spiceIn）
- `netlist_samples/rc_cascade.scs`——Spectre 输出（通过 `maeCreateNetlistForCorner` 导出）
- `netlist_samples/rc_cascade.connectivity.txt`——原理图读取（来自 `02_read_connectivity.py`，所有 3 个层次级别）

## 示例

- `examples/01_virtuoso/schematic/02_read_connectivity.py`——通过 SKILL 读取原理图连接
- `examples/01_virtuoso/schematic/08_import_cdl_cap_array.py`——CDL → spiceIn 导入
- `examples/01_virtuoso/maestro/04_rc_filter_sweep.py`——包含通过 maeCreateNetlistForCorner 的 Spectre 网表导出
