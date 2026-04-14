# 对话框关闭功能实现计划

> **适用于智能体工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 来逐步实现此计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** 通过 X11 自动检测并关闭阻塞的 Virtuoso GUI 对话框，绕过卡住的 SKILL 通道。

**架构：** 当 SKILL `execute_skill()` 调用超时时，通常是因为模态对话框（例如 "Save Changes"、"Warning"）阻塞了 CIW 事件循环。由于 SKILL 通道已失效，我们使用直接的 SSH 来：（1）找到 Virtuoso 进程的 DISPLAY，（2）通过 `xwininfo` 定位对话框窗口，（3）通过远程机器上的 Python2 + ctypes XTest 发送 Enter/Escape 按键。作为 Python API 方法（VirtuosoClient 上）和 CLI 命令 `virtuoso-bridge dismiss-dialog` 两种方式暴露。

**技术栈：** Python、SSH（通过现有 SSHRunner）、远程 Python2 + ctypes（Xlib/XTest）、xwininfo

---

### 任务 1：远程 X11 辅助脚本

一个上传到远程机器的 Python2 脚本，执行实际的 X11 工作：查找对话框窗口、拍摄可选截图、发送按键。这是唯一在远程运行的代码；其他都是本地编排。

**文件：**
- 创建：`src/virtuoso_bridge/resources/x11_dismiss_dialog.py`

- [ ] **步骤 1：创建远程辅助脚本**

```python
#!/usr/bin/env python2
"""X11 对话框查找和关闭器。运行在远程 Virtuoso 主机上。

用法：
    python2 x11_dismiss_dialog.py <DISPLAY> [--dismiss] [--screenshot /tmp/out.ppm]

输出（stdout）：JSON 行，每行一个找到的对话框：
    {"window_id": "0x2e01f16", "title": "Save Changes", "x": 1010, "y": 378, "w": 239, "h": 142}

带 --dismiss：向找到的每个对话框发送 Enter 键。
带 --screenshot：将全屏截图保存为指定路径的 PPM。

退出码：0 = 找到/关闭了对话框，1 = 未找到对话框，2 = 错误
"""
import ctypes
import ctypes.util
import json
import os
import struct
import subprocess
import sys

DIALOG_TITLES = ["Save Changes", "Warning", "Error", "Confirm", "Question"]


def find_display(user=None):
    """如果未提供，则从正在运行的 virtuoso 进程自动检测 DISPLAY。"""
    try:
        pids = subprocess.check_output(
            ["pgrep", "-u", user or os.environ["USER"], "-x", "virtuoso"],
            stderr=subprocess.PIPE
        ).strip().split("\n")
        for pid in pids:
            env_file = "/proc/%s/environ" % pid.strip()
            try:
                data = open(env_file, "rb").read()
                for chunk in data.split(b"\x00"):
                    if chunk.startswith(b"DISPLAY="):
                        return chunk.split(b"=", 1)[1].decode()
            except (IOError, OSError):
                continue
    except (subprocess.CalledProcessError, OSError):
        pass
    return None


def find_dialogs(display):
    """使用 xwininfo 查找与已知标题匹配的对话框窗口。"""
    os.environ["DISPLAY"] = display
    try:
        tree = subprocess.check_output(
            ["xwininfo", "-root", "-tree"],
            stderr=subprocess.PIPE
        ).decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, OSError) as e:
        print(json.dumps({"error": "xwininfo failed: %s" % str(e)}))
        return []

    dialogs = []
    for line in tree.splitlines():
        for title in DIALOG_TITLES:
            if ('"%s"' % title) in line:
                # 解析：0x2e01f16 "Save Changes": ("virtuoso" "virtuoso")  239x142+1+38  +1010+378
                parts = line.strip().split()
                if len(parts) >= 1:
                    win_id = parts[0]
                    # 通过 xwininfo -id 获取几何信息
                    try:
                        info = subprocess.check_output(
                            ["xwininfo", "-id", win_id],
                            stderr=subprocess.PIPE
                        ).decode("utf-8", errors="replace")
                        x = y = w = h = 0
                        for il in info.splitlines():
                            il = il.strip()
                            if il.startswith("Absolute upper-left X:"):
                                x = int(il.split(":")[1].strip())
                            elif il.startswith("Absolute upper-left Y:"):
                                y = int(il.split(":")[1].strip())
                            elif il.startswith("Width:"):
                                w = int(il.split(":")[1].strip())
                            elif il.startswith("Height:"):
                                h = int(il.split(":")[1].strip())
                        dialogs.append({
                            "window_id": win_id,
                            "title": title,
                            "x": x, "y": y, "w": w, "h": h,
                        })
                    except (subprocess.CalledProcessError, OSError):
                        dialogs.append({"window_id": win_id, "title": title})
                break
    return dialogs


def dismiss_window(display, win_id_str):
    """通过 XTest 向窗口发送 Enter 键。"""
    os.environ["DISPLAY"] = display
    xlib_path = ctypes.util.find_library("X11")
    xtst_path = ctypes.util.find_library("Xtst")
    if not xlib_path or not xtst_path:
        return {"error": "libX11 or libXtst not found"}

    xlib = ctypes.cdll.LoadLibrary(xlib_path)
    xtst = ctypes.cdll.LoadLibrary(xtst_path)

    dpy = xlib.XOpenDisplay(None)
    if not dpy:
        return {"error": "cannot open display %s" % display}

    win_id = int(win_id_str, 16) if win_id_str.startswith("0x") else int(win_id_str)

    # 提升并聚焦对话框
    xlib.XRaiseWindow(dpy, win_id)
    xlib.XSetInputFocus(dpy, win_id, 1, 0)  # RevertToParent
    xlib.XFlush(dpy)

    import time
    time.sleep(0.1)

    # 发送 Return 键
    keysym_return = 0xff0d
    keycode = xlib.XKeysymToKeycode(dpy, keysym_return)
    xtst.XTestFakeKeyEvent(dpy, keycode, True, 0)
    xtst.XTestFakeKeyEvent(dpy, keycode, False, 0)
    xlib.XFlush(dpy)

    xlib.XCloseDisplay(dpy)
    return {"dismissed": win_id_str, "keycode": keycode}


def screenshot_ppm(display, output_path):
    """拍摄全屏截图，保存为 PPM。"""
    os.environ["DISPLAY"] = display
    try:
        subprocess.check_call(
            ["xwd", "-root", "-silent", "-out", "/tmp/_vb_screen.xwd"],
            stderr=subprocess.PIPE
        )
    except (subprocess.CalledProcessError, OSError) as e:
        return {"error": "xwd failed: %s" % str(e)}

    # 将 XWD 转换为 PPM
    data = open("/tmp/_vb_screen.xwd", "rb").read()
    hs = struct.unpack(">I", data[0:4])[0]
    w = struct.unpack(">I", data[16:20])[0]
    h = struct.unpack(">I", data[20:24])[0]
    bpp = struct.unpack(">I", data[44:48])[0]
    bpl = struct.unpack(">I", data[48:52])[0]
    pixels = data[hs:]

    rgb = bytearray()
    for y_row in range(h):
        row = pixels[y_row * bpl: y_row * bpl + w * (bpp // 8)]
        for x_col in range(w):
            if bpp == 32:
                b, g, r = ord(row[x_col*4]), ord(row[x_col*4+1]), ord(row[x_col*4+2])
            else:
                b, g, r = ord(row[x_col*3]), ord(row[x_col*3+1]), ord(row[x_col*3+2])
            rgb.append(r)
            rgb.append(g)
            rgb.append(b)

    with open(output_path, "wb") as f:
        f.write("P6\n%d %d\n255\n" % (w, h))
        f.write(bytes(rgb))

    try:
        os.remove("/tmp/_vb_screen.xwd")
    except OSError:
        pass
    return {"screenshot": output_path, "size": [w, h]}


def main():
    args = sys.argv[1:]
    display = None
    do_dismiss = False
    screenshot_path = None

    i = 0
    while i < len(args):
        if args[i] == "--dismiss":
            do_dismiss = True
        elif args[i] == "--screenshot":
            i += 1
            screenshot_path = args[i] if i < len(args) else "/tmp/_vb_screenshot.ppm"
        elif not args[i].startswith("-"):
            display = args[i]
        i += 1

    if not display:
        display = find_display()
        if not display:
            print(json.dumps({"error": "cannot detect DISPLAY"}))
            sys.exit(2)

    # 如果请求则截图
    if screenshot_path:
        result = screenshot_ppm(display, screenshot_path)
        print(json.dumps(result))

    # 查找对话框
    dialogs = find_dialogs(display)
    for d in dialogs:
        print(json.dumps(d))

    if not dialogs:
        sys.exit(1)

    # 如果请求则关闭
    if do_dismiss:
        for d in dialogs:
            if "window_id" in d:
                result = dismiss_window(display, d["window_id"])
                print(json.dumps(result))

    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 2：提交**

```bash
git add src/virtuoso_bridge/resources/x11_dismiss_dialog.py
git commit -m "feat: add remote X11 dialog finder/dismisser script"
```

---

### 任务 2：Python API — VirtuosoClient 上的 `dismiss_dialog()` 方法

通过 SSH 上传辅助脚本，运行并解析结果。作为 `client.dismiss_dialog()` 暴露。

**文件：**
- 创建：`src/virtuoso_bridge/virtuoso/x11.py`
- 修改：`src/virtuoso_bridge/virtuoso/basic/bridge.py`

- [ ] **步骤 1：创建 x11.py 模块**

```python
"""通过 SSH 进行 X11 对话框检测和关闭（绕过 SKILL 通道）。"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from virtuoso_bridge.transport.ssh import SSHRunner

logger = logging.getLogger(__name__)

_HELPER_SCRIPT = Path(__file__).parent.parent / "resources" / "x11_dismiss_dialog.py"
_REMOTE_SCRIPT = "/tmp/virtuoso_bridge_{user}/x11_dismiss_dialog.py"


def _ensure_helper(runner: SSHRunner, user: str) -> str:
    """如果不存在则上传辅助脚本。"""
    remote_path = _REMOTE_SCRIPT.format(user=user)
    remote_dir = str(Path(remote_path).parent)
    runner.run_command(f"mkdir -p {remote_dir}")
    runner.upload(_HELPER_SCRIPT, remote_path)
    return remote_path


def find_dialogs(runner: SSHRunner, user: str, display: str | None = None) -> list[dict[str, Any]]:
    """在远程 X11 显示上查找阻塞对话框窗口。

    参数：
        runner：连接到远程主机的 SSHRunner。
        user：远程用户名（用于进程发现）。
        display：X11 DISPLAY 字符串。如果为 None，则从 virtuoso 进程自动检测。

    返回：
        对话框字典列表：[{"window_id", "title", "x", "y", "w", "h"}, ...]
    """
    script = _ensure_helper(runner, user)
    cmd = f"python2 {script}"
    if display:
        cmd += f" {display}"
    result = runner.run_command(cmd, timeout=15)
    return _parse_output(result.stdout)


def dismiss_dialogs(
    runner: SSHRunner,
    user: str,
    display: str | None = None,
) -> list[dict[str, Any]]:
    """查找并关闭所有阻塞对话框窗口。

    返回：
        结果字典列表（找到的对话框 + 关闭结果）。
    """
    script = _ensure_helper(runner, user)
    cmd = f"python2 {script} --dismiss"
    if display:
        cmd += f" {display}"
    result = runner.run_command(cmd, timeout=15)
    return _parse_output(result.stdout)


def screenshot(
    runner: SSHRunner,
    user: str,
    local_path: str | Path,
    display: str | None = None,
) -> dict[str, Any]:
    """拍摄全屏 X11 截图，下载为 PNG。

    参数：
        local_path：保存截图的本地路径（将为 PNG）。
    """
    script = _ensure_helper(runner, user)
    remote_ppm = f"/tmp/virtuoso_bridge_{user}/x11_screenshot.ppm"
    cmd = f"python2 {script} --screenshot {remote_ppm}"
    if display:
        cmd += f" {display}"
    result = runner.run_command(cmd, timeout=30)
    parsed = _parse_output(result.stdout)

    # 下载 PPM 并在本地转换为 PNG
    local_path = Path(local_path)
    local_ppm = local_path.with_suffix(".ppm")
    runner.download(remote_ppm, str(local_ppm))

    # 将 PPM 转换为 PNG
    try:
        from PIL import Image
        img = Image.open(str(local_ppm))
        img.save(str(local_path))
        local_ppm.unlink(missing_ok=True)
        info = {"local_path": str(local_path), "format": "png"}
    except ImportError:
        info = {"local_path": str(local_ppm), "format": "ppm", "note": "install Pillow for PNG"}

    return {**info, "remote_results": parsed}


def _parse_output(stdout: str) -> list[dict[str, Any]]:
    """解析辅助脚本的 JSON 行输出。"""
    results = []
    for line in (stdout or "").strip().splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except (json.JSONDecodeError, ValueError):
                logger.debug("Non-JSON line from helper: %s", line)
    return results
```

- [ ] **步骤 2：将 `dismiss_dialog()` 和 `x11_screenshot()` 添加到 VirtuosoClient**

在 `src/virtuoso_bridge/virtuoso/basic/bridge.py` 中添加方法：

```python
# 在顶部添加导入：
from virtuoso_bridge.virtuoso import x11

# 将方法添加到 VirtuosoClient 类：

def dismiss_dialog(self, display: str | None = None) -> list[dict]:
    """通过 X11 查找并关闭阻塞 GUI 对话框（绕过 SKILL 通道）。

    当 execute_skill() 因模态对话框阻塞 CIW 而超时时使用。
    通过直接 SSH + X11 工作，独立于 SKILL 通道。

    返回：
        找到/关闭的对话框信息字典列表。
    """
    runner = self.ssh_runner
    if runner is None:
        raise RuntimeError("No SSH connection available (tunnel not started?)")
    user = os.getenv("VB_REMOTE_USER", "")
    return x11.dismiss_dialogs(runner, user, display)

def x11_screenshot(self, local_path: str, display: str | None = None) -> dict:
    """拍摄远程显示的全屏 X11 截图。

    通过直接 SSH 工作，独立于 SKILL 通道。
    """
    runner = self.ssh_runner
    if runner is None:
        raise RuntimeError("No SSH connection available (tunnel not started?)")
    user = os.getenv("VB_REMOTE_USER", "")
    return x11.screenshot(runner, user, local_path, display)
```

- [ ] **步骤 3：提交**

```bash
git add src/virtuoso_bridge/virtuoso/x11.py src/virtuoso_bridge/virtuoso/basic/bridge.py
git commit -m "feat: add dismiss_dialog() and x11_screenshot() to VirtuosoClient"
```

---

### 任务 3：CLI 命令 — `virtuoso-bridge dismiss-dialog`

添加子命令到 CLI，以便用户可以从终端运行。

**文件：**
- 修改：`src/virtuoso_bridge/cli.py`

- [ ] **步骤 1：添加 CLI 函数并注册命令**

在 `cli.py` 中添加处理函数：

```python
def cli_dismiss_dialog(args: argparse.Namespace) -> int:
    """查找并关闭阻塞的 Virtuoso GUI 对话框。"""
    from virtuoso_bridge.virtuoso import x11
    from virtuoso_bridge.transport.ssh import SSHRunner

    profile = _CLI_PROFILE[0] if _CLI_PROFILE else None
    suffix = f"_{profile}" if profile else ""
    remote_host = os.getenv(f"VB_REMOTE_HOST{suffix}", "").strip()
    remote_user = os.getenv(f"VB_REMOTE_USER{suffix}", "").strip()
    jump_host = os.getenv(f"VB_JUMP_HOST{suffix}", "").strip() or None
    jump_user = os.getenv(f"VB_JUMP_USER{suffix}", remote_user).strip() or None
    display = getattr(args, "display", None)

    if not remote_host:
        print("Error: VB_REMOTE_HOST not set")
        return 1

    runner = SSHRunner(
        remote_host=remote_host,
        remote_user=remote_user,
        jump_host=jump_host,
        jump_user=jump_user,
    )

    # 截图模式
    if getattr(args, "screenshot", None):
        print(f"[screenshot] Capturing remote display ...")
        result = x11.screenshot(runner, remote_user, args.screenshot, display)
        print(f"[screenshot] {result.get('local_path', 'unknown')}")
        return 0

    # 查找/关闭模式
    scan_only = getattr(args, "scan", False)
    if scan_only:
        print("[scan] Looking for dialog windows ...")
        dialogs = x11.find_dialogs(runner, remote_user, display)
    else:
        print("[dismiss] Looking for and dismissing dialog windows ...")
        dialogs = x11.dismiss_dialogs(runner, remote_user, display)

    if not dialogs:
        print("No dialog windows found.")
        return 1

    for d in dialogs:
        if "error" in d:
            print(f"  Error: {d['error']}")
        elif "dismissed" in d:
            print(f"  Dismissed: {d['dismissed']}")
        elif "title" in d:
            print(f"  Found: \"{d['title']}\" at ({d.get('x',0)},{d.get('y',0)}) {d.get('w',0)}x{d.get('h',0)}")

    return 0
```

在 `build_parser()` 中添加子解析器：

```python
p_dismiss = sub.add_parser("dismiss-dialog", help="Find and dismiss blocking Virtuoso GUI dialogs")
p_dismiss.add_argument("--scan", action="store_true", help="Only scan for dialogs, don't dismiss")
p_dismiss.add_argument("--display", help="X11 DISPLAY (auto-detected if omitted)")
p_dismiss.add_argument("--screenshot", metavar="PATH", help="Save fullscreen screenshot instead")
```

在调度字典中添加：

```python
"dismiss-dialog": cli_dismiss_dialog,
```

- [ ] **步骤 2：提交**

```bash
git add src/virtuoso_bridge/cli.py
git commit -m "feat: add 'virtuoso-bridge dismiss-dialog' CLI command"
```

---

### 任务 4：集成测试 — 端到端验证

**文件：**
- 创建：`examples/01_virtuoso/basic/07_dismiss_dialog.py`

- [ ] **步骤 1：创建示例脚本**

```python
#!/usr/bin/env python3
"""演示 X11 对话框检测和关闭。

用法：

    python 07_dismiss_dialog.py              # 扫描对话框
    python 07_dismiss_dialog.py --dismiss    # 扫描并关闭
    python 07_dismiss_dialog.py --screenshot # 拍摄全屏截图

前置条件：
  - virtuoso-bridge 服务正在运行（virtuoso-bridge start）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from virtuoso_bridge import VirtuosoClient


def main() -> int:
    client = VirtuosoClient.from_env()

    if "--screenshot" in sys.argv:
        out = Path("output/x11_screenshot.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        result = client.x11_screenshot(str(out))
        print(f"Screenshot: {result}")
        return 0

    if "--dismiss" in sys.argv:
        results = client.dismiss_dialog()
        print(f"Dismiss results: {results}")
    else:
        # 只是检查 — 直接导入 x11 以进行仅扫描模式
        from virtuoso_bridge.virtuoso import x11
        runner = client.ssh_runner
        user = client._tunnel._ssh_runner._remote_user
        dialogs = x11.find_dialogs(runner, user)
        print(f"Dialogs found: {dialogs}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **步骤 2：测试扫描模式（预期无对话框）**

```bash
python examples/01_virtuoso/basic/07_dismiss_dialog.py
# 预期："Dialogs found: []"
```

- [ ] **步骤 3：测试截图**

```bash
python examples/01_virtuoso/basic/07_dismiss_dialog.py --screenshot
# 预期："Screenshot: {'local_path': 'output/x11_screenshot.png', ...}"
```

- [ ] **步骤 4：提交**

```bash
git add examples/01_virtuoso/basic/07_dismiss_dialog.py
git commit -m "feat: add dialog dismiss example script"
```

---

### 任务 5：更新技能文档

**文件：**
- 修改：`skills/virtuoso/references/troubleshooting.md`
- 修改：`skills/virtuoso/SKILL.md`

- [ ] **步骤 1：在故障排除文档中添加 dismiss-dialog**

在 troubleshooting.md 中添加关于对话框阻塞恢复的部分：

```markdown
### GUI 对话框阻塞 — 恢复

当 `execute_skill()` 超时且 SKILL 通道无响应时，
模态对话框可能阻塞了 CIW 事件循环。

**Python API 恢复：**
```python
# 通过 X11 关闭所有阻塞对话框（绕过 SKILL）
results = client.dismiss_dialog()

# 或者先拍摄截图查看发生了什么
client.x11_screenshot("debug_screen.png")
```

**CLI 恢复：**
```bash
virtuoso-bridge dismiss-dialog              # 查找并关闭
virtuoso-bridge dismiss-dialog --scan       # 仅扫描
virtuoso-bridge dismiss-dialog --screenshot output.png  # 截图
```

**预防：** 在 `hiCloseWindow(win)` 之前始终执行 `dbSave(cv)` 以避免 "Save Changes" 对话框。
```

- [ ] **步骤 2：在 SKILL.md Gotchas 部分添加简要说明**

- [ ] **步骤 3：提交**

```bash
git add skills/virtuoso/references/troubleshooting.md skills/virtuoso/SKILL.md
git commit -m "docs: add dialog dismissal to troubleshooting"
```
