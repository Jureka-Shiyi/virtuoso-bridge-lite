# 运行仿真 → 等待 → 读取结果

## 功能概述

这是 RC 滤波器仿真的第二步：
1. 运行仿真
2. 等待完成
3. 读取结果
4. 导出波形数据

## 使用方法

```bash
python 06b_rc_simulate_and_read.py <LIB>
```

**前置条件**：先运行 `06a_rc_create.py <LIB>` 创建电路和设置。

## 代码逻辑解析

### 确保 GUI 打开

```python
def ensure_gui(client):
    # 检查是否有已存在的有效 session
    r = client.execute_skill('''
let((s) s = nil
  foreach(x maeGetSessions() unless(s when(maeGetSetup(?session x) s = x)))
  s)
''')
    session = (r.output or "").strip('"')

    if session and session != "nil":
        save_setup(client, LIB, CELL)
        return

    # 无效 session，重新打开
    client.execute_skill(f'deOpenCellView("{LIB}" "{CELL}" "maestro" "maestro" nil "r")')
    client.execute_skill('maeMakeEditable()')
```

### 运行仿真

```python
r = client.execute_skill('maeRunSimulation()')
run_name = (r.output or "").strip('"')
print(f"[sim] Started: {run_name}")
```

### 等待完成

```python
wait_until_done(client, timeout=600)
```

**重要**：不要在 Maestro 调用中使用 `?waitUntilDone t`，这会导致死锁。应使用异步运行 + `wait_until_done()`。

### 读取结果

```python
results = read_results(client, session, lib=LIB, cell=CELL)
for key, (expr, raw) in results.items():
    print(f"[{key}] {expr}")
    print(f"  {raw}")
```

### 导出波形

```python
export_waveform(client, session, 'dB20(mag(v("/OUT")))',
                mag_file, analysis="ac", history=history)
export_waveform(client, session, 'phase(v("/OUT"))',
                phase_file, analysis="ac", history=history)
```

### 解析结果计算 -3dB 频率

```python
for i, (f, db) in enumerate(data):
    if db <= -3.0:
        # 线性插值计算精确的 -3dB 点
        f_3db = f_prev + ratio * (f - f_prev)
        print(f"  f_3dB = {f_3db:.3e} Hz")
        break
```

## 输出内容

```
=== Results ===
[maeGetOverallYield] ...
  ...

=== Waveforms ===
AC magnitude: .../rc_ac_mag_db.txt
AC phase: .../rc_ac_phase.txt

=== 1000 frequency points ===

=== f_3dB = 1.592e+05 Hz
```

## 前置条件

- `virtuoso-bridge start` 已运行
- 先运行 `06a_rc_create.py <LIB>`
