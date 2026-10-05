# -*- coding: utf-8 -*-
"""
لوحة تحكم الشبكة المصغرة - النسخة الاحترافية
"""
import os
import subprocess
import secrets
import platform
import socket
from datetime import datetime

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

APP_NAME = "لوحة تحكم الشبكة المصغرة"
APP_VERSION = "3.0"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=3600 * 24)

templates = Jinja2Templates(directory="templates")

PRESET_COMMANDS = {
    "Custom Command": None,
    "IP عام": "curl -s --max-time 5 ifconfig.me || echo 'فشل'",
    "IP المحلي": "ip addr show 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}'",
    "Ping google": "ping -c 4 google.com",
    "Traceroute": "traceroute -m 10 google.com 2>/dev/null || echo 'غير مثبت'",
    "DNS lookup": "nslookup google.com 2>/dev/null || getent hosts google.com",
    "WHOIS": "whois google.com 2>/dev/null | head -20 || echo 'غير مثبت'",
    "Route": "ip route",
    "حالة الاتصال": "ping -c 1 8.8.8.8 > /dev/null 2>&1 && echo '✅ متصل' || echo '❌ غير متصل'",
    "ARP devices": "ip neigh show 2>/dev/null | head -20",
    "Network stats": "cat /proc/net/dev",
    "Disk usage": "df -h",
    "Memory": "free -h",
    "Processes": "ps aux | head -15",
    "Uptime": "uptime",
    "CPU info": "cat /proc/cpuinfo | grep -E 'model name|Hardware' | head -3",
    "Kernel": "uname -a",
    "Date": "date",
    "User": "whoami && id",
    "Temperature": "cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 'غير متاح'",
    "Python version": "python --version",
    "Pip packages": "pip list 2>/dev/null | head -15",
    "Git version": "git --version",
    "Files in home": "ls -la ~/",
    "Files current": "ls -la",
    "Biggest files": "du -sh ~/* 2>/dev/null | sort -h | tail -10",
    "Generate password": "cat /dev/urandom | tr -dc 'A-Za-z0-9!@#$%' | head -c 20; echo",
    "HTTP test": "curl -s -o /dev/null -w 'Status: %{http_code}\\n' https://google.com",
    "SSL check": "echo | openssl s_client -connect google.com:443 -servername google.com 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo 'غير مثبت'",
}

BLOCKED_PATTERNS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", ":(){",
    "shutdown", "reboot", "poweroff", "init 0", "init 6",
    "chmod -R 777 /", "chown -R", "kill -9 1", "killall",
]

def is_blocked(cmd: str) -> bool:
    cmd_lower = cmd.lower()
    return any(b in cmd_lower for b in BLOCKED_PATTERNS)

def run_shell(cmd: str, timeout: int = 15) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out, err = r.stdout.strip(), r.stderr.strip()
        if out and err:
            return out + "\n--- stderr ---\n" + err
        return out or err or "(لا يوجد مخرجات)"
    except subprocess.TimeoutExpired:
        return f"⏱ انتهت المهلة ({timeout} ثانية)"
    except Exception as e:
        return f"❌ خطأ: {e}"

def is_authenticated(request: Request) -> bool:
    return request.session.get("auth") is True

def get_system_stats() -> dict:
    stats = {"app": APP_VERSION, "time": datetime.now().strftime("%H:%M:%S")}
    try:
        stats["hostname"] = socket.gethostname()
        with open("/proc/uptime") as f:
            up = float(f.read().split()[0])
            stats["uptime"] = f"{int(up//86400)}ي {int((up%86400)//3600)}س"
        with open("/proc/loadavg") as f:
            stats["load"] = f.read().split()[0]
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                if ":" in line:
                    parts = line.split(":", 1)
                    mem[parts[0].strip()] = parts[1].strip()
            total = int(mem.get("MemTotal", "0").split()[0])
            avail = int(mem.get("MemAvailable", "0").split()[0])
            stats["memory_pct"] = round((total - avail) / total * 100, 1) if total else 0
        stats["platform"] = platform.system()
        stats["python"] = platform.python_version()
    except Exception as e:
        stats["error"] = str(e)
    return stats

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["auth"] = True
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request=request, name="login.html",
        context={"error": "❌ كلمة السر غلط"}, status_code=401,
    )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/health")
async def health():
    return {"status": "ok", "version": APP_VERSION, "time": datetime.now().isoformat()}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "output": None,
            "selected": "Custom Command",
            "custom_cmd": "",
            "commands": list(PRESET_COMMANDS.keys()),
            "stats": get_system_stats(),
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
        },
    )

@app.post("/run", response_class=HTMLResponse)
async def run_cmd(
    request: Request,
    choice: str = Form("Custom Command"),
    custom_cmd: str = Form(""),
):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    if choice == "Custom Command" or choice not in PRESET_COMMANDS:
        cmd = custom_cmd.strip()
    else:
        cmd = PRESET_COMMANDS[choice]
    if is_blocked(cmd):
        output = "🚫 هذا الأمر محظور لأسباب أمنية"
    elif not cmd:
        output = "⚠ لم تُدخل أي أمر"
    else:
        output = f"$ {cmd}\n\n" + run_shell(cmd)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "output": output,
            "selected": choice,
            "custom_cmd": custom_cmd,
            "commands": list(PRESET_COMMANDS.keys()),
            "stats": get_system_stats(),
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
        },
    )

@app.get("/stats")
async def stats():
    return JSONResponse(get_system_stats())

@app.get("/favicon.ico")
async def favicon():
    return HTMLResponse(status_code=204)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    print("\n" + "=" * 60)
    print(f"  🌐 {APP_NAME}")
    print(f"  🔐 كلمة السر: {ADMIN_PASSWORD}")
    print(f"  🔗 http://0.0.0.0:{port}")
    print("=" * 60 + "\n")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False, log_level="info")
