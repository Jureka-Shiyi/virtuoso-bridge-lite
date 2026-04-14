# 复制测试台到另一个库

在工作流中复制测试台 + Maestro 设置到新库。

## 步骤 1：复制 DUT 单元

```python
# dbCopyCellView 需要 db 对象作为第一个参数，不是字符串
client.execute_skill(
    'dbCopyCellView(dbOpenCellViewByType("SRC_LIB" "MY_DUT" "schematic") '
    '"DST_LIB" "MY_DUT" "schematic")')
client.execute_skill(
    'dbCopyCellView(dbOpenCellViewByType("SRC_LIB" "MY_DUT" "symbol") '
    '"DST_LIB" "MY_DUT" "symbol")')
```

## 步骤 2：创建测试台原理图

使用 `schematic.edit()` + `inst()` + `label_term()`。然后通过 CDF 设置每个实例的源参数——**不要**使用 `schHiReplace` 匹配 `cellName`，因为那会匹配该单元类型的所有实例。

```python
# 正确：按名称在特定实例上设置参数
client.execute_skill(
    'let((cv inst cdf p) '
    'cv=dbOpenCellViewByType("LIB" "CELL" "schematic" "schematic" "a") '
    'inst=car(setof(x cv~>instances x~>name=="V8")) '
    'cdf=cdfGetInstCDF(inst) p=cdfFindParamByName(cdf "vdc") '
    'p~>value="Vcm")')

# 错误：用 cellName 匹配 schHiReplace——会将所有 vsin 实例设置为相同值
# schHiReplace(?replaceAll t ?propName "cellName" ?condOp "==" ?propValue "vsin" ...)
```

**重要：** 总是使用 `dbOpenCellViewByType(lib cell "schematic" "schematic" "a")` 而不是 `geGetEditCellView()`。后者取决于当前 GUI 窗口焦点，当 Maestro 或其他非原理图窗口活动时会失败。

## 步骤 3：CDF 参数名称注意事项

CDF 参数名称与 Spectre 网表参数名称不同：

| analogLib 单元 | CDF 参数 | Spectre 网表参数 |
|----------------|-----------|----------------------|
| vsin | `vdc` | `sinedc`（网表生成器自动映射） |
| vsin | `va` | `ampl` |
| vsin | `sinephase` | `sinephase` |
| vsin | `freq` | `freq` |
| vdc | `vdc` | `dc` |
| idc | `idc` | `dc` |
| cap | `c` | `c` |

设置前总是用 `cdfGetInstCDF(inst)~>parameters` 检查实际的 CDF 参数名称。

## 步骤 4：创建 Maestro

对 `maeSetAnalysis` 使用 `.il` 文件（选项列表需要反引号语法）。Python `execute_skill()` 无法可靠处理反引号 + 嵌套引号。

```python
# 创建会话 + 测试
session = open_session(client, LIB, CELL)  # 创建空的 maestro
client.execute_skill(f'maeCreateTest("TEST_NAME" ?session "{session}" '
                     f'?lib "{LIB}" ?cell "{CELL}" ?view "schematic")')

# 通过 Python 设置变量
maeSetVar("Fs", "1G", ?session session)

# 通过 .il 文件设置分析（反引号语法）
client.load_il("setup_tran.il")  # 包含 maeSetAnalysis(test "tran" ?enable t ?options `(...))

# 通过 Python 设置输出（每个需要一个唯一名称，不是 nil）
maeAddOutput("VOUTP", test, ?outputType "net" ?signalName "/VOUTP")
```

**分析选项：使用裸变量名，不是 `VAR("...")`。**
`VAR()` 是一个 Maestro 运行时函数，**不会**转换为 Spectre 网表。网表生成器期望裸变量名（例如 `t_end`，不是 `VAR("t_end")`）。

## 步骤 5：运行仿真

`maeRunSimulation` 需要 GUI Maestro 窗口——首先用 `deOpenCellView` 打开。
`maeWaitUntilDone` 不可靠——改为通过 SSH 轮询 spectre.out。

```python
# 在 GUI 中打开 Maestro（maeRunSimulation 必需）
client.execute_skill('deOpenCellView("LIB" "CELL" "maestro" "maestro" nil "a")')

# 运行
client.execute_skill(f'maeRunSimulation(?session "{session}")')

# 通过 SSH 轮询完成（可靠）
import time
for i in range(120):
    r = runner.run_command(f'grep "completes" {sim_dir}/spectre.out 2>/dev/null || echo running')
    if "completes" in r.stdout:
        break
    time.sleep(5)
```

## 关键陷阱

| 陷阱 | 症状 | 修复 |
|------|------|------|
| `maeAddOutput` 带 nil 名称 | `argument #1 should be a string` | 每个输出需要一个字符串名称 |
| tran 选项中的 `VAR("x")` | Spectre 中 `Function 'VAR' is not defined` | 使用裸变量名 `x` |
| `maeRunSimulation` 返回 nil | 没有 GUI Maestro 窗口打开 | 首先用 `deOpenCellView(... "maestro" ...)` 打开 |
| 删除打开 Maestro 的单元 | 崩溃 / 对话框风暴 | 清除原理图实例而不是删除单元 |
| `geGetEditCellView` 窗口错误 | `cdfGetInstCDF(nil)` 错误 | 使用带显式 lib/cell 的 `dbOpenCellViewByType` |
| `maeOpenSetup` 空测试列表 | `maeGetSetup` 返回 nil | 在 `maeOpenSetup` 后调用 `maeCreateTest` |
| `maeWaitUntilDone` 返回 nil | 后台会话，或仿真已完成 | 改为通过 SSH 轮询 spectre.out |
| 按 cellName 的 `schHiReplace` | 设置该单元类型的所有实例 | 通过 `cdfGetInstCDF` 按实例设置 |
| CDF `va` vs 网表 `ampl` | 参数名称错误，值未设置 | 用 `cdfGetInstCDF(inst)~>parameters` 检查 CDF 名称 |
