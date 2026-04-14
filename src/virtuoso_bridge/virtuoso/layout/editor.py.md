# Layout 编辑器

## 功能概述

批量 SKILL 操作的上下文管理器。用于在 Virtuoso Layout 编辑器中批量执行操作。

## LayoutEditor 类

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `client` | `VirtuosoClient` | - | Virtuoso 客户端 |
| `lib` | `str` | - | 库名 |
| `cell` | `str` | - | Cell 名 |
| `view` | `str` | `"layout"` | 视图名 |
| `mode` | `str` | `"w"` | 打开模式 |
| `timeout` | `int` | `60` | 超时时间（秒） |

### 核心方法

| 方法 | 说明 |
|------|------|
| `add(skill_cmd)` | 添加 SKILL 命令到批处理 |
| `close()` | 添加关闭 cellview 操作 |

### 使用示例

```python
from virtuoso_bridge.virtuoso.layout.editor import LayoutEditor
from virtuoso_bridge.virtuoso.layout.ops import (
    layout_create_rect,
    layout_create_param_inst,
    layout_create_via_by_name,
)

with client.layout.edit("myLib", "myCell") as lay:
    # 添加矩形
    lay.add(layout_create_rect("M1", "drawing", 0, 0, 1, 0.5))
    # 添加参数化实例
    lay.add(layout_create_param_inst(
        "tsmcN28", "nch_ulvt_mac", "layout", "M0", 0, 0, "R0"
    ))
    # 添加通孔
    lay.add(layout_create_via_by_name("M1_M2", 0.5, 0.25))
# 自动执行: dbSave on exit
```

## 错误处理

- SKILL 执行失败时抛出 `RuntimeError`
- 异常时跳过保存（不执行 dbSave）

## 状态管理

- 成功退出：执行 `dbSave()` 保存修改
- 异常退出：不保存，向上传播异常
