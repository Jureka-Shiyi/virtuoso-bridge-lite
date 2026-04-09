#!/usr/bin/env python2
"""X11 dialog finder and dismisser. Runs on the remote Virtuoso host.

Usage:
    python2 x11_dismiss_dialog.py [DISPLAY] [--dismiss]

Output (stdout): JSON lines, one per dialog found:
    {"window_id": "0x2e01f16", "title": "Save Changes", "x": 1010, "y": 378, "w": 239, "h": 142}

With --dismiss: sends Enter key to each dialog found.
DISPLAY auto-detected from running virtuoso process if omitted.

Exit codes: 0 = dialogs found/dismissed, 1 = no dialogs found, 2 = error
"""
import ctypes
import ctypes.util
import json
import os
import subprocess
import sys
import time

DIALOG_TITLES = ["Save Changes", "Warning", "Error", "Confirm", "Question",
                 "Discard", "Overwrite", "Not Found", "Information"]


def find_x11_env(user=None):
    """Auto-detect DISPLAY and XAUTHORITY from running virtuoso process.

    Skips batch virtuoso processes (those with -nograph in cmdline).
    If multiple candidates, prefers the interactive one.
    """
    candidates = []
    try:
        pids = subprocess.check_output(
            ["pgrep", "-u", user or os.environ.get("USER", ""), "-x", "virtuoso"],
            stderr=subprocess.PIPE
        ).strip().split("\n")
        for pid in pids:
            pid = pid.strip()
            if not pid:
                continue
            # Skip batch processes (have -nograph in cmdline)
            try:
                cmdline = open("/proc/%s/cmdline" % pid, "rb").read()
                if b"-nograph" in cmdline:
                    continue
            except (IOError, OSError):
                pass
            env_file = "/proc/%s/environ" % pid
            try:
                data = open(env_file, "rb").read()
                info = {"DISPLAY": None, "XAUTHORITY": None}
                for chunk in data.split(b"\x00"):
                    if chunk.startswith(b"DISPLAY="):
                        info["DISPLAY"] = chunk.split(b"=", 1)[1].decode()
                    elif chunk.startswith(b"XAUTHORITY="):
                        info["XAUTHORITY"] = chunk.split(b"=", 1)[1].decode()
                if info["DISPLAY"]:
                    candidates.append(info)
            except (IOError, OSError):
                continue
    except (subprocess.CalledProcessError, OSError):
        pass

    if not candidates:
        return {"DISPLAY": None, "XAUTHORITY": None}

    # Prefer interactive display (not Xvfb-style small displays)
    # Heuristic: Xvfb displays often use high display numbers (:99, :1024)
    # Real user sessions use lower numbers or localhost:NN
    return candidates[0]


def find_dialogs(display):
    """Use xwininfo to find dialog windows matching known titles."""
    os.environ["DISPLAY"] = display
    try:
        tree = subprocess.check_output(
            ["xwininfo", "-root", "-tree"],
            stderr=subprocess.PIPE
        ).decode("utf-8", "replace")
    except (subprocess.CalledProcessError, OSError) as e:
        print(json.dumps({"error": "xwininfo failed: %s" % str(e)}))
        return []

    dialogs = []
    for line in tree.splitlines():
        for title in DIALOG_TITLES:
            if ('"%s"' % title) in line:
                parts = line.strip().split()
                if len(parts) < 1:
                    break
                win_id = parts[0]
                try:
                    info = subprocess.check_output(
                        ["xwininfo", "-id", win_id],
                        stderr=subprocess.PIPE
                    ).decode("utf-8", "replace")
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
    """Send Enter key to a window via XTest."""
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

    xlib.XRaiseWindow(dpy, win_id)
    xlib.XSetInputFocus(dpy, win_id, 1, 0)  # RevertToParent
    xlib.XFlush(dpy)

    time.sleep(0.15)

    keysym_return = 0xff0d  # XK_Return
    keycode = xlib.XKeysymToKeycode(dpy, keysym_return)
    xtst.XTestFakeKeyEvent(dpy, keycode, True, 0)
    xtst.XTestFakeKeyEvent(dpy, keycode, False, 0)
    xlib.XFlush(dpy)

    xlib.XCloseDisplay(dpy)
    return {"dismissed": win_id_str, "keycode": int(keycode)}


def main():
    args = sys.argv[1:]
    display = None
    do_dismiss = False

    i = 0
    while i < len(args):
        if args[i] == "--dismiss":
            do_dismiss = True
        elif not args[i].startswith("-"):
            display = args[i]
        i += 1

    if not display:
        x11_env = find_x11_env()
        display = x11_env.get("DISPLAY")
        if not display:
            print(json.dumps({"error": "cannot detect DISPLAY"}))
            sys.exit(2)
        if x11_env.get("XAUTHORITY"):
            os.environ["XAUTHORITY"] = x11_env["XAUTHORITY"]
    dialogs = find_dialogs(display)
    for d in dialogs:
        print(json.dumps(d))

    if not dialogs:
        sys.exit(1)

    if do_dismiss:
        for d in dialogs:
            if "window_id" in d:
                result = dismiss_window(display, d["window_id"])
                print(json.dumps(result))

    sys.exit(0)


if __name__ == "__main__":
    main()
