# -*- coding: utf-8 -*-
"""
لوحة تحكم الشبكة المصغرة (Meraki Style)
FastAPI + Jinja2 + Uvicorn
متوافق مع Python 3.14
"""
import subprocess
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="Network Panel")
templates = Jinja2Templates(directory="templates")

# ==================== أوامر جاهزة ====================
PRESET_COMMANDS = {
    "Custom Command": None,
    "ifconfig": "ifconfig",
    "ip addr": "ip addr",
    "netstat": "netstat -tuln",
    "ping google": "ping -c 4 google.com",
    "DNS lookup": "nslookup google.com",
    "public IP": "curl -s ifconfig.me",
    "disk usage": "df -h",
    "memory": "free -h",
    "processes": "ps aux | head -20",
    "uptime": "uptime",
}


def run_shell(cmd: str, timeout: int = 15) -> str:
    """ينفّذ أمر shell بشكل آمن مع timeout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if out and err:
            return out + "\n--- stderr ---\n" + err
        return out or err or "(لا يوجد مخرجات)"
    except subprocess.TimeoutExpired:
        return f"⏱ انتهت المهلة ({timeout} ثانية) — الأمر استغرق وقتاً طويلاً"
    except Exception as e:
        return f"❌ خطأ: {e}"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "output": None,
            "selected": "Custom Command",
            "custom_cmd": "",
            "commands": list(PRESET_COMMANDS.keys()),
        },
    )


@app.post("/run", response_class=HTMLResponse)
async def run_cmd(
    request: Request,
    choice: str = Form("Custom Command"),
    custom_cmd: str = Form(""),
):
    # تحديد الأمر الفعلي
    if choice == "Custom Command" or choice not in PRESET_COMMANDS:
        cmd = custom_cmd.strip()
    else:
        cmd = PRESET_COMMANDS[choice]

    # حماية بسيطة: منع أوامر خطيرة
    blocked = ["rm -rf /", "mkfs", "dd if=", ":(){", "shutdown", "reboot"]
    if any(b in cmd for b in blocked):
        output = "🚫 هذا الأمر محظور لأسباب أمنية"
    elif not cmd:
        output = "⚠ لم تُدخل أي أمر"
    else:
        output = f"$ {cmd}\n\n" + run_shell(cmd)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "output": output,
            "selected": choice,
            "custom_cmd": custom_cmd,
            "commands": list(PRESET_COMMANDS.keys()),
        },
    )


@app.get("/favicon.ico")
async def favicon():
    return HTMLResponse(status_code=204)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  🌐 لوحة تحكم الشبكة المصغرة")
    print("  افتح: http://127.0.0.1:8081")
    print("=" * 50 + "\n")
    import os
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
