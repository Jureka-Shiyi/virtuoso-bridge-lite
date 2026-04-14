# Resources 资源文件模块

## 功能概述

virtuoso-bridge 的资源文件目录，包含辅助脚本等资源。

## 内容

本模块为包目录标识，不包含可导入的 Python 代码。

## 资源文件

### x11_dismiss_dialog.py

X11 对话框关闭辅助脚本，用于在 Virtuoso CIW 被模态对话框阻塞时，通过 X11 直接操作关闭对话框。

```python
from virtuoso_bridge.transport.ssh import SSHRunner
from virtuoso_bridge.virtuoso.x11 import dismiss_dialogs

runner = SSHRunner(host="server", user="zhangz")
results = dismiss_dialogs(runner, "zhangz")
```

此脚本被 `virtuoso/x11.py` 模块使用，无需单独调用。
