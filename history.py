# -*- coding: utf-8 -*-
"""سجل الأوامر"""
import json
import os
from collections import deque
from config import MAX_HISTORY

HISTORY_FILE = os.path.expanduser("~/.netpanel_history.json")


def load_history() -> list:
    """تحميل السجل من الملف"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history: list):
    """حفظ السجل في الملف"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-MAX_HISTORY:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add_to_history(command: str, output: str, success: bool = True):
    """إضافة أمر للسجل"""
    history = load_history()
    history.append({
        "command": command,
        "output": output[:2000],
        "success": success,
        "timestamp": __import__("time").time(),
    })
    save_history(history)


def clear_history():
    """مسح السجل"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
