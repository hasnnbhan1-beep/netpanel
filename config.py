# -*- coding: utf-8 -*-
"""إعدادات التطبيق"""
import os

# كلمة السر (غيّرها!)
ADMIN_PASSWORD = os.environ.get("PANEL_PASSWORD", "admin123")

# مفتاح الجلسات السري (غيّره!)
SECRET_KEY = os.environ.get("PANEL_SECRET", "change-this-to-random-string-xyz-123")

# مدة الجلسة (بالثواني) — 24 ساعة
SESSION_TIMEOUT = 60 * 60 * 24

# حد الأوامر المحفوظة في السجل
MAX_HISTORY = 50

# منع الأوامر الخطيرة
BLOCKED_COMMANDS = [
    "rm -rf /", "mkfs", "dd if=", ":(){", "shutdown", "reboot",
    "> /dev/sda", "chmod -R 777 /", "mv / ", "mv /*",
]

# الأوامر الجاهزة (مصنّفة)
PRESET_COMMANDS = {
    "🌐 الشبكة": {
        "ifconfig": "ifconfig",
        "ip addr": "ip addr",
        "netstat (المنافذ)": "netstat -tuln",
        "ping Google": "ping -c 4 google.com",
        "traceroute": "traceroute -m 10 google.com",
        "DNS lookup": "nslookup google.com",
        "public IP": "curl -s ifconfig.me",
        "WiFi info": "termux-wifi-connectioninfo 2>/dev/null || echo 'غير متاح'",
        "scan local": "ip neigh show",
    },
    "💻 النظام": {
        "uptime": "uptime",
        "disk usage": "df -h",
        "memory": "free -h",
        "processes (top 20)": "ps aux | head -20",
        "CPU info": "cat /proc/cpuinfo | head -30",
        "OS info": "uname -a",
        "battery": "termux-battery-status 2>/dev/null || echo 'غير متاح'",
        "date": "date",
        "env vars": "env | sort | head -30",
    },
    "📂 الملفات": {
        "list home": "ls -lah ~",
        "list sdcard": "ls -lah /sdcard 2>/dev/null | head -20",
        "current dir": "pwd",
        "disk space home": "du -sh ~/* 2>/dev/null | sort -h | tail -10",
        "recent files": "find ~ -type f -mtime -1 2>/dev/null | head -20",
    },
    "🔧 أدوات": {
        "python version": "python --version",
        "pip list (top)": "pip list 2>/dev/null | head -20",
        "git version": "git --version",
        "curl test": "curl -s -I https://google.com | head -5",
    },
    "✏️ Custom Command": {
        "Custom Command": None,
    },
}
