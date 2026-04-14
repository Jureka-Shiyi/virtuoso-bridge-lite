# Maestro 会话管理

## 功能概述

Maestro (ADE Assembler) 会话管理：打开、关闭、查找后台会话。

## 主要函数

### `open_session(client, lib, cell) -> str`

通过 `maeOpenSetup` 在后台打开 maestro，返回 session 字符串。

```python
from virtuoso_bridge.virtuoso.maestro.session import open_session

session = open_session(client, "myLib", "myTestbench")
print(f"Opened session: {session}")
```

### `close_session(client, session) -> None`

通过 `maeCloseSession` 关闭后台 maestro 会话。

```python
close_session(client, session)
```

### `find_open_session(client) -> str | None`

查找第一个有效测试的活动会话，返回 session 字符串或 None。

```python
session = find_open_session(client)
if session:
    print(f"Found active session: {session}")
```

## 返回值

- `session`: 会话字符串（如 "maestro"），用于后续的 `maeGetSetup`、`maeSetAnalysis` 等调用

## 注意

- `maeOpenSetup` 在后台打开会话，不阻塞
- `maeCloseSession` 会取消任何进行中的仿真
