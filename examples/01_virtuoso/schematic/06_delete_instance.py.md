# 删除原理图中的实例

## 功能概述

本脚本从当前打开的原理图中删除第一个实例。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个有多于一个实例的原理图
python 06_delete_instance.py
```

## 代码逻辑解析

### 列出当前实例

```python
r = client.execute_skill('''
let((cv out)
  cv = geGetEditCellView()
  out = ""
  foreach(inst cv~>instances
    out = strcat(out inst~>name "\\n"))
  out)
''')
names = [n for n in raw.splitlines() if n]
print(f"Instances: {names}")
```

### 保存、删除、保存

```python
target = names[0]
client.execute_skill(f'''
let((cv inst)
  cv = geGetEditCellView()
  schCheck(cv) dbSave(cv)
  inst = car(setof(x cv~>instances x~>name == "{target}"))
  when(inst dbDeleteObject(inst))
  schCheck(cv) dbSave(cv)
  sprintf(nil "deleted: {target}"))
''')
```

**关键**：删除前保存，删除后再次保存，确保数据库一致性。

## 删除操作

```python
dbDeleteObject(inst)
```

从数据库中删除指定对象。

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- Virtuoso 中有打开的原理图
