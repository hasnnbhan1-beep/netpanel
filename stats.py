# -*- coding: utf-8 -*-
"""إحصائيات النظام"""
import subprocess


def get_system_stats() -> dict:
    """جلب إحصائيات النظام"""
    stats = {
        "cpu": "—",
        "memory": "—",
        "disk": "—",
        "uptime": "—",
        "load": "—",
    }

    # Uptime & Load
    try:
        with open("/proc/loadavg", "r") as f:
            parts = f.read().split()
            stats["load"] = f"{parts[0]} / {parts[1]} / {parts[2]}"
    except Exception:
        pass

    try:
        result = subprocess.run(["uptime", "-p"], capture_output=True, text=True, timeout=3)
        stats["uptime"] = result.stdout.strip() or "—"
    except Exception:
        pass

    # Memory
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = parts[1].strip()
            total = int(meminfo.get("MemTotal", "0").split()[0])
            avail = int(meminfo.get("MemAvailable", "0").split()[0])
            used = total - avail
            pct = round(used / total * 100, 1) if total else 0
            stats["memory"] = f"{pct}% ({used // 1024}MB / {total // 1024}MB)"
    except Exception:
        pass

    # Disk
    try:
        result = subprocess.run(
            ["df", "-h", "/data"], capture_output=True, text=True, timeout=3
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 5:
                stats["disk"] = f"{parts[4]} ({parts[2]} / {parts[1]})"
    except Exception:
        pass

    return stats
