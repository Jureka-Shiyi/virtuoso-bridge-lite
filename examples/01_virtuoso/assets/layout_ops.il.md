# layout_ops.il

## 功能概述

提供布局（Layout）操作的辅助函数，包括读取布局、删除形状、保存和删除 Cell 等。

## 函数列表

### 内部函数

#### `_LayoutGetEditCV()`

获取当前打开的布局窗口的 editable cellview。

```skill
_LayoutGetEditCV()
```

**返回值**：当前布局的 cellview，失败返回 `nil`

---

### `LayoutReadLayout(libName cellName)`

读取布局的形状和实例摘要信息（只读）。

```skill
LayoutReadLayout(libName cellName)
```

**返回值**：格式化的布局信息字符串

**输出格式**：
```
Layout: myLib/myCell/layout  (10 shapes  3 instances)
  rect [M1 drawing]  (0.000 0.000)-(10.000 5.000)
  inst: NMOS0  [technology/nch]  @ (5.000 2.500)
```

---

### `LayoutListShapes()`

列出当前打开布局中的所有 shapes。

```skill
LayoutListShapes()
```

**返回值**：格式化的 shapes 列表

---

### `LayoutSave()`

保存当前打开的布局。

```skill
LayoutSave()
```

**返回值**：`"saved: libName/cellName"` 或错误信息

---

### `LayoutDeleteShapesOnLayer(layer purpose)`

删除指定层/目的的所有 shapes。

```skill
LayoutDeleteShapesOnLayer(layer purpose)
```

**返回值**：删除的 shapes 数量和状态信息

---

### `LayoutClearRouting()`

删除所有 shapes（保留 instances），然后保存。

```skill
LayoutClearRouting()
```

**返回值**：删除的 shapes 数量和状态信息

---

### `LayoutDeleteCell(libName cellName)`

关闭并删除指定的 layout cell。

```skill
LayoutDeleteCell(libName cellName)
```

**返回值**：删除结果或错误信息

## 代码解析

### 获取编辑中的 CellView

```skill
procedure(_LayoutGetEditCV()
  let((cv)
    cv = nil
    foreach(win hiGetWindowList()
      when(!cv && win~>cellView && win~>cellView~>viewName == "layout"
        cv = dbOpenCellViewByType(
               win~>cellView~>libName win~>cellView~>cellName
               "layout" "maskLayout" "a")))
    cv))
```

遍历窗口列表，查找 layout 视图并以追加模式打开。

### 形状删除逻辑

```skill
foreach(shape shapes
  when(car(shape~>lpp) == layer && cadr(shape~>lpp) == purpose
    dbDeleteObject(shape)
    count = count + 1))
```

使用 layer/purpose 匹配要删除的 shapes。

## 使用示例

```python
# 列出当前布局的 shapes
result = client.execute_skill("LayoutListShapes()")

# 删除 M3 层的所有 shapes
result = client.execute_skill('LayoutDeleteShapesOnLayer("M3" "drawing")')

# 清除所有 routing（保留 instances）
result = client.execute_skill("LayoutClearRouting()")
```

## 对应的 Python API

| IL 函数 | Python 方法 |
|--------|------------|
| `LayoutListShapes()` | `client.layout.list_shapes()` |
| `LayoutDeleteShapesOnLayer()` | `client.layout.delete_shapes_on_layer()` |
| `LayoutClearRouting()` | `client.layout.clear_routing()` |
| `LayoutDeleteCell()` | `client.layout.delete_cell()` |
| `LayoutSave()` | `client.save_current_cellview()` |
