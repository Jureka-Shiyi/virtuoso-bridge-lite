"""X11 dialog detection and dismissal via SSH (bypasses SKILL channel).

When a modal dialog blocks the Virtuoso CIW event loop, all execute_skill()
calls time out.  This module uses direct SSH + remote Python2/Xlib to find
and dismiss those dialogs without touching the SKILL channel.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import os

from virtuoso_bridge.transport.ssh import SSHRunner

logger = logging.getLogger(__name__)

_HELPER_SCRIPT = Path(__file__).parent.parent / "resources" / "x11_dismiss_dialog.py"


def _get_display(display: str | None) -> str | None:
    """Resolve display: explicit arg > VB_DISPLAY env var > auto-detect (None)."""
    if display:
        return display
    return os.getenv("VB_DISPLAY") or None


def _ensure_helper(runner: SSHRunner, user: str) -> str:
    """Upload the helper script if not already present."""
    remote_path = f"/tmp/virtuoso_bridge_{user}/x11_dismiss_dialog.py"
    remote_dir = str(Path(remote_path).parent)
    runner.run_command(f"mkdir -p {remote_dir}")
    runner.upload(_HELPER_SCRIPT, remote_path)
    return remote_path


def find_dialogs(
    runner: SSHRunner,
    user: str,
    display: str | None = None,
) -> list[dict[str, Any]]:
    """Find blocking dialog windows on the remote X11 display.

    Returns list of dicts: [{"window_id", "title", "x", "y", "w", "h"}, ...]
    """
    script = _ensure_helper(runner, user)
    resolved = _get_display(display)
    cmd = f"python2 {script}"
    if resolved:
        cmd += f" {resolved}"
    result = runner.run_command(cmd, timeout=15)
    return _parse_output(result.stdout)


def dismiss_dialogs(
    runner: SSHRunner,
    user: str,
    display: str | None = None,
) -> list[dict[str, Any]]:
    """Find and dismiss all blocking dialog windows.

    Returns list of result dicts (found dialogs + dismissal results).
    """
    script = _ensure_helper(runner, user)
    resolved = _get_display(display)
    cmd = f"python2 {script} --dismiss"
    if resolved:
        cmd += f" {resolved}"
    result = runner.run_command(cmd, timeout=15)
    return _parse_output(result.stdout)


def screenshot(
    runner: SSHRunner,
    user: str,
    local_path: str | Path,
    display: str | None = None,
) -> dict[str, Any]:
    """Take a fullscreen X11 screenshot, download as PNG (or PPM).

    Args:
        local_path: Local path to save the screenshot (PNG if Pillow installed).
    """
    script = _ensure_helper(runner, user)
    resolved = _get_display(display)
    remote_ppm = f"/tmp/virtuoso_bridge_{user}/x11_screenshot.ppm"
    cmd = f"python2 {script} --screenshot {remote_ppm}"
    if resolved:
        cmd += f" {resolved}"
    result = runner.run_command(cmd, timeout=30)
    parsed = _parse_output(result.stdout)

    local_path = Path(local_path)
    local_ppm = local_path.with_suffix(".ppm")
    local_ppm.parent.mkdir(parents=True, exist_ok=True)
    runner.download(remote_ppm, local_ppm)

    try:
        from PIL import Image
        img = Image.open(str(local_ppm))
        img.save(str(local_path))
        local_ppm.unlink(missing_ok=True)
        info: dict[str, Any] = {"local_path": str(local_path), "format": "png"}
    except ImportError:
        info = {"local_path": str(local_ppm), "format": "ppm",
                "note": "install Pillow for PNG conversion"}

    return {**info, "remote_results": parsed}


def _parse_output(stdout: str) -> list[dict[str, Any]]:
    """Parse JSON-lines output from the helper script."""
    results = []
    for line in (stdout or "").strip().splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except (json.JSONDecodeError, ValueError):
                logger.debug("Non-JSON line from helper: %s", line)
    return results
