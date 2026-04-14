# 打开 Maestro → 读取配置 → 关闭窗口

## 功能概述

本脚本展示完整的 Maestro 工作流程：
1. 在 GUI 中打开 Maestro 视图
2. 读取配置信息
3. 关闭窗口（不保存）

## 使用方法

```bash
python 02_gui_open_read_close_maestro.py <LIB>
```

## 代码逻辑解析

### 步骤 1: 打开 Maestro

```python
r = client.execute_skill(f'''
let((before after session)
  before = maeGetSessions()
  deOpenCellView("{LIB}" "{CELL}" "maestro" "maestro" nil "r")
  after = maeGetSessions()
  session = nil
  foreach(s after unless(member(s before) session = s))
  session
)
''')
session = (r.output or "").strip('"')
```

使用 `deOpenCellView()` 在 GUI 中打开 Maestro。

### 步骤 2: 读取配置

```python
for key, (skill_expr, raw) in read_config(client, session).items():
    print(f"[{key}] {skill_expr}")
    print(raw)
```

### 步骤 3: 关闭窗口

```python
client.execute_skill(f'''
foreach(win hiGetWindowList()
  let((n) n = hiGetWindowName(win)
    when(and(n rexMatchp("{CELL}" n) rexMatchp("maestro" n))
      errset(hiCloseWindow(win))
      let((form) form = hiGetCurrentForm()
        when(form errset(hiFormCancel(form)))
      )
    )
  )
)
''')
```

遍历窗口列表，关闭匹配的 Maestro 窗口，并取消可能存在的表单对话框。

## 注意事项

- 使用 `errset()` 防止关闭操作失败导致脚本中断
- 同时关闭窗口和表单对话框确保干净退出
- 不调用 `dbSave()`，窗口关闭不保存更改

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
