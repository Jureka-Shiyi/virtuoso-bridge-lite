# screenshot.il

## 功能概述

截取当前 Virtuoso 窗口的截图并保存为 PNG 格式。

## 函数

### `takeScreenshot(savePath)`

截取当前窗口图像并保存。

```skill
takeScreenshot(savePath)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `savePath` | 字符串 | 保存路径（必须包含文件名和 .png 扩展名） |

**返回值**：
- 成功：`"Screenshot saved to: <path>"`
- 失败：`"Error: No active window found"`

## 代码解析

```skill
procedure(takeScreenshot(savePath)
    let((window)
        window = hiGetCurrentWindow()
        if(window then
            hiWindowSaveImage(
                ?target window
                ?path savePath
                ?format "png"
                ?toplevel nil
            )
            sprintf(nil "Screenshot saved to: %s" savePath)
        else
            sprintf(nil "Error: No active window found")
        )
    )
)
```

### 关键函数

| 函数 | 作用 |
|------|------|
| `hiGetCurrentWindow()` | 获取当前活动窗口句柄 |
| `hiWindowSaveImage()` | 保存窗口图像 |

### `hiWindowSaveImage()` 参数

| 参数 | 说明 |
|------|------|
| `?target` | 目标窗口对象 |
| `?path` | 保存路径 |
| `?format` | 图像格式（`"png"`, `"jpg"`, `"xwd"` 等） |
| `?toplevel` | 是否包含顶层窗口 |

## 使用示例

### Python 调用

```python
from virtuoso_bridge import VirtuosoClient
from pathlib import Path

client = VirtuosoClient.from_env()

# 加载截图辅助脚本
IL_FILE = Path(__file__).parent.parent / "assets" / "screenshot.il"
client.load_il(IL_FILE)

# 执行截图
remote_path = "/tmp/virtuoso_bridge/screenshots/layout_20260414.png"
result = client.execute_skill(f'takeScreenshot("{remote_path}")')

# 下载到本地
local_path = Path("output/screenshot.png")
client.download_file(remote_path, local_path)
```

### 完整流程

```
1. client.load_il(screenshot.il)  → 上传脚本到远程
2. SSH mkdir -p /tmp/.../screenshots  → 创建目录
3. takeScreenshot("/path/to/save.png")  → 截图保存到远程
4. client.download_file(remote, local)  → 下载到本地
```

## 支持的窗口类型

- Layout 窗口
- Schematic 窗口
- Library Manager 窗口
- Maestro 窗口

## 注意事项

- 路径必须可写
- 必须有打开的窗口，否则返回错误
- 默认保存为 PNG 格式（无损压缩）
- 截图保存在远程主机，需要下载到本地

## 用途

- 自动化测试中记录设计状态
- 调试时保存窗口快照
- 生成文档插图
