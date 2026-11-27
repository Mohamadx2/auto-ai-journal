"""
Core activity tracker for Auto AI Journal.

Polls the currently focused window, maps it to a category,
accumulates time, and writes daily Markdown + JSON + TXT journals.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import signal
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml
from platformdirs import user_documents_dir

# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------

def get_active_window() -> Tuple[Optional[str], Optional[str]]:
    """
    Return (process_name, window_title) of the currently focused window.
    Returns (None, None) on failure or unsupported platform.
    """
    system = platform.system()

    if system == "Windows":
        try:
            import win32gui
            import win32process
            import psutil

            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None, None

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                process_name = proc.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = None

            title = win32gui.GetWindowText(hwnd) or ""
            return process_name, title
        except Exception:
            return None, None

    elif system == "Darwin":  # macOS
        try:
            from AppKit import NSWorkspace
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID,
            )

            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            process_name = active_app.get("NSApplicationName", "").lower()

            # Best-effort window title
            windows = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            )
            title = ""
            for win in windows:
                if win.get("kCGWindowOwnerName") == active_app.get("NSApplicationName"):
                    title = win.get("kCGWindowName", "") or ""
                    break
            return process_name, title
        except Exception:
            return None, None

    else:  # Linux and others – best effort with psutil + xdotool if available
        try:
            import subprocess
            import psutil

            # Try xdotool first (common on Linux desktops)
            try:
                window_id = subprocess.check_output(
                    ["xdotool", "getactivewindow"], text=True
                ).strip()
                title = subprocess.check_output(
                    ["xdotool", "getwindowname", window_id], text=True
                ).strip()
                pid = int(
                    subprocess.check_output(
                        ["xdotool", "getwindowpid", window_id], text=True
                    ).strip()
                )
                process_name = psutil.Process(pid).name().lower()
                return process_name, title
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

            # Fallback: just the most CPU-hungry process (very rough)
            return None, None
        except Exception:
            return None, None


def categorize(process_name: Optional[str], title: Optional[str], rules: dict) -> str:
    """Map process + title to a friendly category."""
    if not process_name and not title:
        return "unknown"

    text = f"{process_name or ''} {title or ''}".lower()

    for category, keywords in rules.items():
        for kw in keywords:
            if kw.lower() in text:
                return category
    return "other"


# ---------------------------------------------------------------------------
# Journal writer
# ---------------------------------------------------------------------------

class Journal:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.today = date.today()
        self.seconds: Dict[str, float] = defaultdict(float)
        self._load_existing()

    def _paths(self):
        """Return paths for json, md, and txt files (all named with the date)."""
        base = self.output_dir / self.today.isoformat()
        return (
            base.with_suffix(".json"),
            base.with_suffix(".md"),
            base.with_suffix(".txt"),
        )

    def _load_existing(self):
        json_path, _, _ = self._paths()
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                self.seconds = defaultdict(float, data.get("seconds", {}))
            except Exception:
                pass

    def add(self, category: str, delta: float):
        if delta <= 0:
            return
        # Roll over at midnight
        if date.today() != self.today:
            self._flush()
            self.today = date.today()
            self.seconds = defaultdict(float)
        self.seconds[category] += delta

    def _build_activity_lines(self) -> tuple[list[str], float]:
        """Build the list of activity lines and return total hours."""
        lines = []
        total = 0.0
        for cat, secs in sorted(self.seconds.items(), key=lambda x: -x[1]):
            hours = secs / 3600
            total += hours
            if hours >= 0.05:  # only show ≥ 3 minutes
                lines.append(f"- {hours:.1f} hours {cat.replace('_', ' ')}")
        return lines, total

    def _flush(self):
        json_path, md_path, txt_path = self._paths()

        # Structured JSON
        payload = {
            "date": self.today.isoformat(),
            "seconds": dict(self.seconds),
            "updated": datetime.now().isoformat(timespec="seconds"),
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        activity_lines, total = self._build_activity_lines()

        # Human-readable Markdown
        md_lines = [f"## {self.today.isoformat()}\n"]
        md_lines.extend(activity_lines)
        md_lines.append(f"\n**Total tracked active time:** {total:.1f} hours\n")
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        # Plain TXT export (date in filename, clean readable format)
        txt_lines = [
            f"Auto AI Journal – {self.today.isoformat()}",
            "=" * 40,
            "",
        ]
        txt_lines.extend(activity_lines)
        txt_lines.append("")
        txt_lines.append(f"Total tracked active time: {total:.1f} hours")
        txt_lines.append("")
        txt_lines.append(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        txt_path.write_text("\n".join(txt_lines), encoding="utf-8")

    def flush(self):
        self._flush()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def load_config(path: Optional[Path] = None) -> dict:
    if path is None:
        path = Path("config.yaml")
    if not path.exists():
        path = Path("config.example.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Auto AI Journal – background activity diary")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    parser.add_argument("--background", action="store_true", help="Run quietly (less console output)")
    parser.add_argument("--once", action="store_true", help="Sample once and exit (for testing)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    poll = float(cfg.get("poll_interval", 5))
    min_session = float(cfg.get("min_session_seconds", 15))
    rules = cfg.get("categories", {})

    out_dir = Path(os.path.expanduser(cfg.get("output_dir", "~/Documents/AutoAIJournal")))
    journal = Journal(out_dir)

    if not args.background:
        print(f"Auto AI Journal v0.1.0")
        print(f"Logging to: {out_dir}")
        print(f"Polling every {poll}s  (Ctrl+C to stop)\n")

    last_cat: Optional[str] = None
    last_change = time.monotonic()
    accumulated = 0.0

    def shutdown(sig=None, frame=None):
        # Credit remaining time
        if last_cat and accumulated >= min_session:
            journal.add(last_cat, accumulated)
        journal.flush()
        if not args.background:
            print("\nJournal saved. Goodbye.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            proc, title = get_active_window()
            cat = categorize(proc, title, rules)

            now = time.monotonic()
            delta = now - last_change

            if cat != last_cat:
                # Previous category finished
                if last_cat and accumulated >= min_session:
                    journal.add(last_cat, accumulated)
                    if not args.background:
                        print(f"[{datetime.now():%H:%M:%S}] +{accumulated/60:.1f} min → {last_cat}")
                last_cat = cat
                last_change = now
                accumulated = 0.0
            else:
                accumulated += delta
                last_change = now

            # Periodic flush so files stay reasonably up to date
            if int(now) % 60 < poll:  # roughly every minute
                journal.flush()

            if args.once:
                break

            time.sleep(poll)

    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
