# remote_paths 模块

## 功能概述

远程路径解析辅助函数，提供默认远程目录和用户名解析。

## 主要函数

### `default_virtuoso_bridge_dir(username, subdir)`

获取 virtuoso bridge 默认远程目录。

```python
default_virtuoso_bridge_dir("zhangz", "virtuoso_bridge")
# 返回: "/home/zhangz/virtuoso_bridge"
```

### `default_remote_spectre_work_dir(username)`

获取 Spectre 仿真工作目录。

```python
default_remote_spectre_work_dir("zhangz")
# 返回: "/home/zhangz/virtuoso_bridge/spectre_work"
```

### `resolve_remote_username(configured_user, runner)`

解析远程用户名。

**参数**:
- `configured_user`: 配置的用户名
- `runner`: SSHRunner 实例

**返回**: 用户名字符串

通过 SSH 执行 `whoami` 命令获取实际用户名。
