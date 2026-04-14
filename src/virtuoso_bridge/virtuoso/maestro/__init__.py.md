# Maestro 模块

## 功能概述

Maestro (ADE Assembler) 会话管理、配置读写和写入的完整 API。

## 导入

```python
from virtuoso_bridge.virtuoso.maestro import (
    # 会话
    open_session,
    close_session,
    find_open_session,
    # 读取
    read_config,
    read_env,
    read_results,
    export_waveform,
    # 写入 - 测试
    create_test,
    set_design,
    # 写入 - 分析
    set_analysis,
    # 写入 - 输出
    add_output,
    set_spec,
    # 写入 - 变量
    set_var,
    get_var,
    delete_var,
    # 写入 - 参数
    get_parameter,
    set_parameter,
    # 写入 - 环境/仿真选项
    set_env_option,
    set_sim_option,
    # 写入 - 角落
    set_corner,
    load_corners,
    # 写入 - 运行模式
    set_current_run_mode,
    set_job_control_mode,
    set_job_policy,
    # 写入 - 仿真
    run_simulation,
    wait_until_done,
    # 写入 - 导出
    create_netlist_for_corner,
    export_output_view,
    write_script,
    # 写入 - 迁移
    migrate_adel_to_maestro,
    migrate_adexl_to_maestro,
    # 写入 - 保存
    save_setup,
    # 写入 - GUI
    open_maestro_gui_with_history,
)
```

## 使用示例

### 完整仿真流程

```python
from virtuoso_bridge.virtuoso.maestro import (
    open_session, close_session,
    set_analysis, set_var, run_simulation, wait_until_done,
    read_results, save_setup
)

# 打开会话
session = open_session(client, "myLib", "myTestbench")

# 配置仿真
set_analysis(client, "tran", "tran", options='(("stop" "1m"))')
set_var(client, "vdd", "1.8")

# 运行
run_name = run_simulation(client, session=session)
wait_until_done(client, timeout=300)

# 读取结果
results = read_results(client, session)

# 保存
save_setup(client, "myLib", "myTestbench", session=session)

# 关闭会话
close_session(client, session)
```

### 变量 Sweep

```python
from virtuoso_bridge.virtuoso.maestro import set_var

# 扫频
set_var(client, "freq", "1K,10K,100K,1M", type_name="test", type_value='("tran")')
```
