# maestro_utils.il

## 功能概述

提供 Maestro 会话管理的工具函数，包括打开、关闭会话，清除锁文件，处理对话框等。

## 函数列表

### `MaestroDismissDialog()`

关闭当前弹出的任何对话框（Overwrite、Save 等）。

```skill
MaestroDismissDialog()
```

**返回值**：`t`（始终）

---

### `MaestroGetLibPath(libName)`

解析库路径，支持多种 fallback 方式。

```skill
MaestroGetLibPath(libName)
```

**路径解析顺序**：
1. `writePath`
2. `readPath`
3. `libPath`

**返回值**：库路径字符串，失败返回 `nil`

---

### `MaestroFindSessionViews(libName cellName)`

查找 cell 中所有 session 类型的视图。

```skill
MaestroFindSessionViews(libName cellName)
```

**匹配的前缀**：
- `maestro`
- `adexl`
- `normVim`
- `topsim`

**返回值**：匹配的视图名称列表

---

### `MaestroClearLocks(libName cellName)`

清除 cell 的所有 session 视图的锁文件。

```skill
MaestroClearLocks(libName cellName)
```

**锁文件路径**：
```
<libPath>/<cellName>/<viewName>/<viewName>.sdb.cdslck
```

**返回值**：始终返回 `t`

---

### `MaestroOpen(libName cellName [viewName])`

打开 Maestro 会话，确保可编辑状态，返回 session。

```skill
MaestroOpen(libName cellName @optional (viewName "maestro"))
```

**参数**：
- `libName`：库名
- `cellName`：单元名
- `viewName`：视图名（默认 `"maestro"`）

**返回值**：session 标识符

**流程**：
1. 检查是否已有窗口打开
2. 如果未打开，清除锁文件后打开
3. 尝试 `maeMakeEditable()`
4. 如果弹出对话框，关闭后重试
5. 返回可用的 session

---

### `MaestroClose(libName cellName [viewName])`

保存并关闭指定 cell 的 Maestro 窗口。

```skill
MaestroClose(libName cellName @optional (viewName "maestro"))
```

**返回值**：`t`（如果找到并关闭了窗口）

---

### `MaestroCloseAll()`

关闭所有 Maestro 窗口和会话。

```skill
MaestroCloseAll()
```

**返回值**：关闭的窗口数量

## 代码解析

### 对话框关闭

```skill
procedure(MaestroDismissDialog()
  let((form)
    form = hiGetCurrentForm()
    when(form
      hiFormDone(form)
      printf("[MaestroDismissDialog] Dismissed dialog\n")
      t
    )
  )
)
```

### 锁文件清除

```skill
procedure(MaestroClearLocks(libName cellName)
  let((libPath views lockPath)
    libPath = MaestroGetLibPath(libName)
    views = MaestroFindSessionViews(libName cellName)
    unless(views views = '("maestro"))
    foreach(viewName views
      lockPath = sprintf(nil "%s/%s/%s/%s.sdb.cdslck"
                        libPath cellName viewName viewName)
      when(isFile(lockPath)
        deleteFile(lockPath)
        printf("[MaestroClearLocks] Removed %s\n" lockPath))))
    t))
```

## 使用示例

```python
# 打开 Maestro
session = client.execute_skill(
    f'MaestroOpen("{LIB}" "{CELL}")'
).output

# 关闭所有 Maestro
client.execute_skill("MaestroCloseAll()")

# 清除锁文件
client.execute_skill(f'MaestroClearLocks("{LIB}" "{CELL}")')
```

## 对话框处理

> **重要**：在 `maeMakeEditable()` 等操作后可能弹出确认对话框。`MaestroDismissDialog()` 会自动处理这些对话框，防止脚本卡住。

## 用途

- 后台自动化 Maestro 操作
- 处理锁文件冲突
- 批量打开/关闭 Maestro 会话
