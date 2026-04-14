# Maestro 配置写入

## 功能概述

写入 Maestro 配置：创建测试、设置分析、输出、变量、角落、运行仿真等。

## 主要函数

### 测试管理

#### `create_test(client, test, *, lib, cell, view="schematic", simulator="spectre", session="") -> str`

创建新测试。

```python
create_test(client, "AC_test", lib="myLib", cell="myTB")
```

#### `set_design(client, test, *, lib, cell, view="schematic", session="") -> str`

更改现有测试的 DUT。

```python
set_design(client, "AC_test", lib="myLib", cell="myTB")
```

### 分析设置

#### `set_analysis(client, test, analysis, *, enable=True, options="", session="") -> str`

启用/禁用分析并设置选项。

- `options`: SKILL alist 字符串，如 `'(("start" "1") ("stop" "10G") ("dec" "20"))'`

```python
# 设置 AC 分析
set_analysis(client, "AC_test", "ac", options='(("start" "1") ("stop" "10G") ("dec" "20"))')

# 禁用某个分析
set_analysis(client, "AC_test", "noise", enable=False)
```

### 输出管理

#### `add_output(client, name, test, *, output_type="", signal_name="", expr="", session="") -> str`

添加输出（波形或表达式）。

```python
add_output(client, "VOUT", "AC_test", signal_name="VF(\"/VOUT\")")
add_output(client, "gain", "AC_test", expr="dB20(mag(VF(\"/VOUT\")))")
```

#### `set_spec(client, name, test, *, lt="", gt="", session="") -> str`

设置输出的 pass/fail spec。

```python
set_spec(client, "gain", "AC_test", lt="-3")
```

### 变量管理

#### `set_var(client, name, value, *, type_name="", type_value="", session="") -> str`

设置设计变量。

```python
# 全局变量
set_var(client, "vdd", "1.35")

# 测试级变量（parametric sweep）
set_var(client, "f", "100M,2G,4G,8G", type_name="test", type_value='("IB_PSS")')

# 角落变量
set_var(client, "vdd", "1.2 1.4", type_name="corner", type_value='("myCorner")')
```

#### `get_var(client, name, *, session="") -> str`

获取设计变量值。

#### `delete_var(client, name, *, test="", session="") -> str`

删除设计变量。

```python
# 删除全局变量
delete_var(client, "f")

# 删除测试级变量
delete_var(client, "f", test="IB_PSS")
```

### 参数管理（parametric sweep）

#### `set_parameter(client, name, value, *, type_name="", type_value="", session="") -> str`

在全局或角落级别添加或更新参数。

```python
set_parameter(client, "cload", "1p")
set_parameter(client, "cload", "1p 2p", type_name="corner", type_value='("myCorner")')
```

#### `get_parameter(client, name, *, type_name="", type_value="", session="") -> str`

获取参数值。

### 环境选项

#### `set_env_option(client, test, options, *, session="") -> str`

设置环境选项（模型文件、视图列表等）。

```python
set_env_option(client, "AC_test", '(("modelFiles" (("/path/model.scs" "tt"))))')
```

#### `set_sim_option(client, test, options, *, session="") -> str`

设置仿真器选项（reltol, temp 等）。

```python
set_sim_option(client, "AC_test", '(("temp" "85") ("reltol" "1e-5"))')
```

### 角落管理

#### `set_corner(client, name, *, disable_tests="", session="") -> str`

创建或修改角落。

```python
set_corner(client, "typical", disable_tests='("TRAN")')
```

#### `load_corners(client, filepath, *, sections="corners", operation="overwrite") -> str`

从 CSV 文件加载角落。

```python
load_corners(client, "/path/to/corners.csv")
```

### 运行模式

#### `set_current_run_mode(client, run_mode, *, session="") -> str`

切换运行模式。

```python
set_current_run_mode(client, "Single Run, Sweeps and Corners")
```

#### `set_job_control_mode(client, mode, *, session="") -> str`

设置作业控制模式（如 "Local", "LSCS"）。

#### `set_job_policy(client, policy, *, test_name="", job_type="", session="") -> str`

设置测试的作业策略。

### 仿真执行

#### `run_simulation(client, *, session="") -> str`

运行仿真（异步，立即返回）。

```python
run_name = run_simulation(client, session=session)
print(f"Started: {run_name}")
```

#### `wait_until_done(client, timeout=600) -> None`

等待仿真完成。

**重要**: 必须在 `run_simulation()` 之后且 GUI 会话打开时调用。

```python
run_simulation(client, session=session)
wait_until_done(client, timeout=300)
```

### 导出功能

#### `create_netlist_for_corner(client, test, corner, output_dir) -> str`

为角落导出独立网表。

#### `export_output_view(client, filepath, *, view="Detail") -> str`

将结果导出到 CSV。

#### `write_script(client, filepath) -> str`

将整个设置导出为可复现的 SKILL 脚本。

### 迁移

#### `migrate_adel_to_maestro(client, lib, cell, state) -> str`

将 ADE L 状态迁移到 maestro 视图。

#### `migrate_adexl_to_maestro(client, lib, cell, view="adexl", *, maestro_view="maestro") -> str`

将 ADE XL 视图迁移到 maestro 视图。

### 保存和 GUI

#### `save_setup(client, lib, cell, *, session="") -> str`

保存 maestro 设置到磁盘。

```python
save_setup(client, "myLib", "myTB")
```

#### `open_maestro_gui_with_history(client, lib, cell, *, history="") -> str`

打开 Maestro GUI 窗口并显示仿真历史。

```python
history = open_maestro_gui_with_history(client, "myLib", "myTB")
```
