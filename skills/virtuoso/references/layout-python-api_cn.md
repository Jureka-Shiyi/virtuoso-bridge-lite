# Layout Python API

通过 SKILL 控制 Cadence Virtuoso 布局编辑的 Python 封装。

**包：** `virtuoso_bridge.virtuoso.layout`

```python
from virtuoso_bridge import VirtuosoClient
client = VirtuosoClient.from_env()
# LayoutOps 通过 client.layout 访问
```

## LayoutEditor（上下文管理器）

收集 SKILL 命令，在 `__exit__` 时批量执行，然后自动保存。

```python
from virtuoso_bridge.virtuoso.layout import (
    layout_create_rect as rect,
    layout_create_path as path,
    layout_create_param_inst as inst,
    layout_create_via_by_name as via,
)

with client.layout.edit(lib, cell) as lay:
    lay.add(rect("M1", "drawing", 0, 0, 1, 0.5))
    lay.add(path("M2", "drawing", [(0, 0), (1, 0)], 0.1))
    lay.add(inst("tsmcN28", "nch_ulvt_mac", "layout", "M0", 0, 0, "R0"))
    lay.add(via("M1_M2", 0.5, 0.25))
    # dbSave 在退出时自动执行
```

### LayoutEditor 方法

| 方法 | 描述 |
|------|------|
| `add(skill_cmd)` | 排队 SKILL 命令（来自 ops 函数） |
| `close()` | 追加关闭 cellview 命令 |

## SKILL 构建函数（ops）

与 `lay.add(...)` 一起使用：

**创建形状：**

| 函数 | SKILL | 描述 |
|------|-------|------|
| `layout_create_rect(layer, purpose, x1, y1, x2, y2)` | `dbCreateRect` | 矩形 |
| `layout_create_path(layer, purpose, points, width)` | `dbCreatePath` | 带宽度的路径 |
| `layout_create_polygon(layer, purpose, points)` | `dbCreatePolygon` | 多边形 |
| `layout_create_label(layer, purpose, x, y, text, just, rot, font, height)` | `dbCreateLabel` | 文本标签 |

**实例和通孔：**

| 函数 | SKILL | 描述 |
|------|-------|------|
| `layout_create_param_inst(lib, cell, view, name, x, y, orient)` | `dbCreateParamInst` | 放置实例 |
| `layout_create_simple_mosaic(lib, cell, *, origin, rows, cols, ...)` | `dbCreateSimpleMosaic` | Mosaic 阵列 |
| `layout_create_via(via_def_expr, x, y, orient, via_params)` | `dbCreateVia` | 通孔 |
| `layout_create_via_by_name(via_name, x, y, ...)` | 通孔查找 + `dbCreateVia` | 按名称创建通孔 |

**读取：**

| 函数 | SKILL | 描述 |
|------|-------|------|
| `layout_read_summary(lib, cell)` | 实例/形状计数 | 快速概览 |
| `layout_read_geometry(lib, cell)` | 完整几何转储 | 制表符分隔输出 |
| `layout_list_shapes()` | 形状类型和 LPP | 从打开的窗口 |

**编辑：**

| 函数 | SKILL | 描述 |
|------|-------|------|
| `clear_current_layout()` | 删除可见形状 | 清除当前 |
| `layout_clear_routing()` | 删除全部 + 保存 | 清除并保存 |
| `layout_select_box(bbox)` | `geSelectBox` | 框选 |
| `layout_delete_selected()` | `leDeleteAllSelect` | 删除选择 |
| `layout_delete_shapes_on_layer(layer, purpose)` | 遍历 + 删除 | 按层删除 |
| `layout_delete_cell(lib, cell)` | 关闭 + `ddDeleteObj` | 删除单元 |

**层可见性：**

| 函数 | SKILL | 描述 |
|------|-------|------|
| `layout_set_active_lpp(layer, purpose)` | `leSetEntryLayer` | 设置活动层 |
| `layout_show_only_layers(layers)` | 隐藏全部 + 显示 | 显示特定 LPP |
| `layout_show_layers(layers)` | `leSetLayerVisible t` | 显示 LPP |
| `layout_hide_layers(layers)` | `leSetLayerVisible nil` | 隐藏 LPP |
| `layout_highlight_net(net_name)` | `geSelectNet` | 高亮网络 |
| `layout_fit_view()` | `hiZoomAbsoluteScale` | 适应视图 |

## 工具函数

| 函数 | 描述 |
|------|------|
| `parse_layout_geometry_output(raw)` | 将 `layout_read_geometry` 输出解析为 `[{"kind": ..., "bbox": ..., ...}]` |
| `layout_find_via_def(via_name)` | 构建用于按名称查找通孔定义的 SKILL |
| `layout_via_def_expr_from_name(via_name)` | 构建通孔定义查找的 SKILL 表达式 |

### 追加模式

对于大型布局，分块处理：

```python
with client.layout.edit(lib, cell, mode="w") as lay:
    lay.add(rect("M1", "drawing", 0, 0, 10, 0.5))

with client.layout.edit(lib, cell, mode="a") as lay:
    lay.add(rect("M2", "drawing", 0, 1, 10, 1.5))
```
