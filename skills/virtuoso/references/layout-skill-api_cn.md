# Layout 参考

## 编辑模式

```python
from virtuoso_bridge.virtuoso.layout import (
    layout_create_rect as rect,
    layout_create_path as path,
    layout_create_label as label,
    layout_create_polygon as polygon,
    layout_create_param_inst as inst,
    layout_create_via_by_name as via,
    layout_create_simple_mosaic as mosaic,
)

with client.layout.edit(lib, cell, mode="a") as lay:
    lay.add(rect("M1", "drawing", 0, 0, 1, 0.5))
    lay.add(path("M2", "drawing", [(0, 0), (1, 0)], 0.1))
    lay.add(label("M1", "pin", 0.5, 0.25, "VDD", "centerCenter", "R0", "roman", 0.1))
    lay.add(polygon("M3", "drawing", [(0, 0), (1, 0), (1, 1), (0.5, 1.5)]))
    lay.add(inst("tsmcN28", "nch_ulvt_mac", "layout", "M0", 0, 0, "R0"))
    lay.add(via("M1_M2", 0.5, 0.25))
    lay.add(mosaic("tsmcN28", "nch_ulvt_mac", rows=2, cols=4,
                   row_pitch=0.5, col_pitch=1.0))
```

- `mode="w"`：创建新的（覆盖）
- `mode="a"`：追加到现有的

## 读取 / 查询

```python
from virtuoso_bridge.virtuoso.layout import layout_read_geometry, layout_list_shapes, layout_read_summary

r = client.execute_skill(layout_read_geometry(lib, cell))
r = client.execute_skill(layout_list_shapes())
r = client.execute_skill(layout_read_summary(lib, cell))
```

## 控制

```python
from virtuoso_bridge.virtuoso.layout import (
    layout_fit_view, layout_show_only_layers, layout_highlight_net,
    clear_current_layout, layout_clear_routing,
    layout_delete_shapes_on_layer, layout_delete_cell,
)

client.execute_skill(layout_fit_view())
client.execute_skill(layout_show_only_layers([("M1", "drawing"), ("M2", "drawing")]))
client.execute_skill(layout_highlight_net("VDD"))
client.execute_skill(clear_current_layout())
client.execute_skill(layout_delete_shapes_on_layer("M3", "drawing"))
client.execute_skill(layout_delete_cell(lib, cell))
```

## 技巧

- **布线前读取**：使用 `layout_read_geometry()` 获取真实坐标，不要从标签猜测
- **大型编辑**：分成块，首先 `mode="w"`，然后后续批次用 `mode="a"`
- **通孔名称**：不确定时通过 `execute_skill()` 查询 `techGetTechFile(cv)~>viaDefs`
- **Mosaic 间距**：原点到原点的间距，不是边缘间隙。从测量的 bbox 推导
- **金属上的标签**：锚定在金属形状上，不要在旁边
- **编辑后截图**：目视验证几何，不要仅依赖坐标

## 另见

- `references/layout-python-api.md`——Python API 参考
