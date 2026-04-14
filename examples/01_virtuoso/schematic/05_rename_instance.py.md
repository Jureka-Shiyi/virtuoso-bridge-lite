# 重命名原理图中的实例

## 功能概述

本脚本重命名当前打开的原理图中的实例名称，并执行检查和保存。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个原理图
python 05_rename_instance.py
```

## 代码逻辑解析

### 重命名实例

```python
renames = [("I0", "IAAA_RENAMED"), ("R0", "RBBB_RENAMED")]

for old, new in renames:
    r = client.execute_skill(f'''
let((cv inst)
  cv = geGetEditCellView()
  inst = car(setof(x cv~>instances x~>name == "{old}"))
  when(inst inst~>name = "{new}" sprintf(nil "renamed: {old} -> {new}")))
''')
```

使用 `setof()` 查找匹配的实例，然后直接修改 `inst~>name`。

### 检查并保存

```python
client.execute_skill(
    'let((cv) cv = geGetEditCellView() schCheck(cv) dbSave(cv) "saved")')
```

## 关键 SKILL 函数

| 函数 | 作用 |
|------|------|
| `geGetEditCellView()` | 获取当前编辑的 cellview |
| `setof(x list pred)` | 过滤列表 |
| `car()` | 取列表第一个元素 |
| `schCheck()` | 原理图检查 |
| `dbSave()` | 保存数据库 |

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso 中有打开的原理图
