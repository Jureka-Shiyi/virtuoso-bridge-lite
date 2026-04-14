# Layout SKILL 操作构建器

## 功能概述

Layout 编辑的 SKILL 操作构建函数，生成创建图形、实例、通孔等的 SKILL 代码。

## 主要函数

### CellView 绑定

#### `layout_bind_current_or_open_cell_view(lib, cell, *, view="layout", view_type=None, mode="w") -> str`

当匹配时绑定 `cv` 到当前编辑 layout，否则打开它。

### 图形创建

#### `layout_create_rect(layer, purpose, x0, y0, x1, y1, *, cv_expr="cv") -> str`

创建矩形。

```python
layout_create_rect("M1", "drawing", 0, 0, 1, 0.5)
```

#### `layout_create_path(layer, purpose, points, width, style=None, *, cv_expr="cv") -> str`

创建路径。

```python
layout_create_path("M2", "drawing", [(0, 0), (1, 0), (1, 1)], 0.1, style="Flatten")
```

#### `layout_create_polygon(layer, purpose, points, *, cv_expr="cv") -> str`

创建多边形。

```python
layout_create_polygon("M1", "drawing", [(0, 0), (1, 0), (1, 1), (0, 1)])
```

#### `layout_create_label(layer, purpose, x, y, text, justification, rotation, font, height, *, cv_expr="cv") -> str`

创建标签。

```python
layout_create_label("text", "drawing", 0.5, 0.5, "VSS", "centerCenter", "R0", "stick", 0.1)
```

### 通孔创建

#### `layout_create_via(via_def_expr, x, y, orientation, via_params_expr, *, cv_expr="cv") -> str`

创建通孔。

#### `layout_find_via_def(via_name, *, cv_expr="cv") -> str`

按名称解析 cellview techfile 中的通孔定义。

```python
layout_find_via_def("M1_M2", cv_expr="cv")
```

#### `layout_create_via_by_name(via_name, x, y, orientation="R0", via_params_expr="nil", *, cv_expr="cv") -> str`

按名称解析通孔定义并创建通孔。

```python
layout_create_via_by_name("M1_M2", 0.5, 0.25, "R0")
```

### 实例创建

#### `layout_create_param_inst(lib, cell, view, instance_name, x, y, orientation, *, cv_expr="cv") -> str`

通过 master 名称创建参数化实例。

```python
layout_create_param_inst("tsmcN28", "nch_ulvt_mac", "layout", "M0", 0, 0, "R0")
```

#### `layout_create_simple_mosaic(lib, cell, *, origin=(0.0, 0.0), orientation="R0", rows, cols, row_pitch, col_pitch, view="layout", view_type=None, instance_name=None, cv_expr="cv") -> str`

创建简单马赛克。

```python
layout_create_simple_mosaic("basic", "nmos4", rows=4, cols=4, row_pitch=1.0, col_pitch=1.0)
```

### 层操作

#### `layout_set_active_lpp(layer, purpose="drawing") -> str`

设置活动 layout 层-目的对。

```python
layout_set_active_lpp("M1", "drawing")
```

#### `layout_show_only_layers(layers) -> str`

隐藏所有层，然后显示请求的层-目的对。

```python
layout_show_only_layers([("M1", "drawing"), ("M2", "drawing")])
```

#### `layout_show_layers(layers) -> str`

显示特定层-目的对。

#### `layout_hide_layers(layers) -> str`

隐藏特定层-目的对。

### 选择操作

#### `layout_select_box(bbox, *, mode_name="replace", view="layout", view_type=None, mode="a") -> str`

在边界框中选择图形。

- `mode_name`: "replace"（替换选择）、"add"（添加到选择）、"sub"/"subtract"/"remove"（从选择中移除）

```python
layout_select_box((0, 0, 1, 1), mode_name="replace")
```

#### `layout_highlight_net(net_name, *, view="layout", view_type=None, mode="a") -> str`

通过查找该网上的 shape 高亮命名网络。

```python
layout_highlight_net("VDD")
```

#### `layout_delete_selected(*, view="layout", view_type=None, mode="a") -> str`

删除布局窗口中的当前选择。

### 读取操作

#### `layout_read_summary(lib, cell, *, view="layout", view_type=None) -> str`

读取 layout cellview 的图形和实例摘要。

```python
layout_read_summary("myLib", "myCell")
# 返回格式: "Layout: myLib/myCell/layout  (N shapes  M instances)\n  rect [M1 drawing] (0.000 0.000)-(1.000 0.500)\n  inst: M0  [tsmcN28/nch]  @ (0.500 0.250)\n"
```

#### `layout_read_geometry(lib, cell, *, view="layout", view_type=None) -> str`

以可解析的逐行格式转储 layout 几何数据。

```python
layout_read_geometry("myLib", "myCell")
# 返回格式: "shape\tobjType=rect\tlayer=M1\tpurpose=drawing\tbbox=...\tpoints=...\txy=...\torient=...\ttext=...\n"
#           "instance\tname=M0\tlib=tsmcN28\tcell=nch\tview=layout\txy=...\torient=...\tbbox=...\ttransform=...\n"
```

#### `layout_list_shapes(*, view="layout", view_type=None, mode="a") -> str`

列出打开 layout 中的 shape 类型和 LPP。

### 删除操作

#### `layout_delete_shapes_on_layer(layer, purpose="drawing", *, view="layout", view_type=None, mode="a") -> str`

从打开的 layout 中删除给定层/目的上的所有 shape。

```python
layout_delete_shapes_on_layer("M1", "drawing")
```

#### `layout_clear_routing(*, view="layout", view_type=None, mode="a") -> str`

删除打开 layout 中的所有 shape 并保存（保留实例）。

#### `layout_delete_cell(lib, cell) -> str`

关闭 layout 窗口并删除目标 cell。

### 视图操作

#### `layout_fit_view() -> str`

将当前 layout 窗口调整为适应视图。

```python
layout_fit_view()
```
