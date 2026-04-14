# SKILL 脚本组合

## 功能概述

将多个原子 SKILL 命令组合成单个可执行脚本字符串。

## 主要函数

### `compose_skill_script(commands, *, wrap_in_progn=True)`

将原子 SKILL 命令组合成单个脚本。

**参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `commands` | `Iterable[str]` | - | SKILL 命令可迭代对象 |
| `wrap_in_progn` | `bool` | `True` | 是否用 `progn()` 包装 |

**返回**: `str` - 组合后的 SKILL 脚本

**规则**:
- 空命令自动过滤
- 单个命令且 `wrap_in_progn=False` 时直接返回
- 单个 `progn()` 命令直接返回
- 多个命令用换行连接后用 `progn()` 包装

**异常**: `ValueError` - 当没有有效命令时

```python
from virtuoso_bridge.virtuoso.basic.composition import compose_skill_script

# 组合多个命令
script = compose_skill_script([
    'cv = dbOpenCellViewByType("myLib" "myCell" "layout" "maskLayout" "r")',
    'dbSave(cv)',
    'dbClose(cv)'
])

# 不包装
single = compose_skill_script(['printf("hello")'], wrap_in_progn=False)
```
