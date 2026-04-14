# Layout 模块

## 功能概述

Cadence Virtuoso Layout 编辑的 SKILL 构建器和编辑器封装。

## 导出内容

### 类

| 类 | 说明 |
|---|---|
| `LayoutEditor` | Layout 批量编辑的上下文管理器 |
| `LayoutOps` | 挂载在 VirtuosoClient 上的 `client.layout` |

### 几何解析

| 函数 | 说明 |
|------|------|
| `parse_layout_geometry_output` | 解析 `layout_read_geometry` 返回的几何数据 |

### CellView 操作

| 函数 | 说明 |
|------|------|
| `layout_bind_current_or_open_cell_view` | 绑定或打开 layout cellview |
| `close_current_cellview` | 关闭当前 cellview |
| `clear_current_layout` | 删除所有可见图形 |

### 图形创建

| 函数 | 说明 |
|------|------|
| `layout_create_rect` | 创建矩形 |
| `layout_create_path` | 创建路径 |
| `layout_create_polygon` | 创建多边形 |
| `layout_create_label` | 创建标签 |
| `layout_create_via` | 创建通孔 |
| `layout_create_via_by_name` | 按名称创建通孔 |
| `layout_create_param_inst` | 创建参数化实例 |
| `layout_create_simple_mosaic` | 创建简单马赛克 |

### 层操作

| 函数 | 说明 |
|------|------|
| `layout_set_active_lpp` | 设置活动层-目的对 |
| `layout_show_only_layers` | 仅显示指定层 |
| `layout_show_layers` | 显示层 |
| `layout_hide_layers` | 隐藏层 |

### 选择和编辑

| 函数 | 说明 |
|------|------|
| `layout_select_box` | 框选图形 |
| `layout_highlight_net` | 高亮网络 |
| `layout_delete_selected` | 删除选中图形 |
| `layout_delete_shapes_on_layer` | 删除指定层图形 |
| `layout_delete_cell` | 删除 cell |

### 读取

| 函数 | 说明 |
|------|------|
| `layout_read_summary` | 读取布局摘要 |
| `layout_read_geometry` | 读取几何数据 |
| `layout_list_shapes` | 列出 shapes |

### 通孔

| 函数 | 说明 |
|------|------|
| `layout_find_via_def` | 查找通孔定义 |
| `layout_via_def_expr_from_name` | 通孔定义表达式 |

### 其他

| 函数 | 说明 |
|------|------|
| `layout_fit_view` | 适应视图 |
| `layout_clear_routing` | 清除布线（保留实例） |

## 使用示例

```python
from virtuoso_bridge import VirtuosoClient

client = VirtuosoClient.from_env()

# 通过 client.layout 访问 LayoutOps
with client.layout.edit("myLib", "myCell") as lay:
    lay.add(layout_create_rect("M1", "drawing", 0, 0, 1, 0.5))
# 自动保存
```
