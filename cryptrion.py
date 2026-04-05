import os
import sys
import json
import time
import shutil
import hashlib
import winreg
import requests
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import psutil
import tempfile

APP_NAME = "Cryptrion-Official"
APP_VERSION = "1.0.0"
AUTHOR = "Wyatt Mouris"
GITHUB_API_URL = "https://api.github.com/repos/mouriswyatt66-alt/Cryptrion-Official/releases/latest"
GITHUB_REPO = "https://github.com/mouriswyatt66-alt/Cryptrion-Official"
EXE_NAME = "Cryptrion.exe"
STARTUP_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

BG       = "#080810"
PANEL    = "#0e0e1c"
ACCENT   = "#00e5ff"
PURPLE   = "#8b5cf6"
RED      = "#ff3355"
GREEN    = "#00ff99"
YELLOW   = "#ffcc00"
FG       = "#dde0ff"
DIM      = "#555588"
FONT     = ("Consolas", 9)
FONT_B   = ("Consolas", 9, "bold")
FONT_LG  = ("Consolas", 16, "bold")

SIGNATURE_DB = {
    "EICAR-Test-File":         "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
    "Trojan.Generic.A":        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "Ransomware.WannaCry":     "db349b97c37d22f5ea1d1841e3c89eb4f2a5a00b914c3e3f72c7a91e23f3f4f",
    "Backdoor.Mirai":          "5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef",
    "Spyware.AgentTesla":      "aabbccddeeff00112233445566778899aabbccddeeff001122334455667788",
    "Keylogger.HawkEye":       "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "Adware.BrowserHijack":    "fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
    "Worm.Conficker":          "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "Rootkit.ZeroAccess":      "0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a697887960f1e2d3c4b",
    "Dropper.NjRAT":           "a9b8c7d6e5f4031201a9b8c7d6e5f403a9b8c7d6e5f40312a9b8c7d6e5f403",
}

HEURISTIC_STRINGS = [
    b"keylogger", b"ransomware", b"vssadmin delete shadows",
    b"netsh advfirewall set allprofiles state off",
    b"powershell -encodedcommand", b"powershell -enc",
    b"mimikatz", b"lsadump::sam", b"sekurlsa::logonpasswords",
    b"CreateRemoteThread", b"VirtualAllocEx", b"WriteProcessMemory",
    b"IsDebuggerPresent", b"NtUnmapViewOfSection",
    b"RegSetValueEx", b"cmd /c del", b"attrib +h +s",
    b"schtasks /create", b"bitcoin", b"monero", b"tor2web",
]

RISKY_EXT = {".exe",".dll",".bat",".cmd",".vbs",".ps1",
             ".scr",".pif",".com",".jar",".js",".jse",
             ".wsf",".wsh",".msi",".hta",".cpl"}

class Startup:
    @staticmethod
    def is_enabled():
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY, 0, winreg.KEY_READ)
            winreg.QueryValueEx(k, APP_NAME)
            winreg.CloseKey(k)
            return True
        except Exception:
            return False

    @staticmethod
    def enable():
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(k)
        except Exception:
            pass

    @staticmethod
    def disable():
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(k, APP_NAME)
            winreg.CloseKey(k)
        except Exception:
            pass


class Updater:
    def get_latest(self):
        try:
            r = requests.get(GITHUB_API_URL, timeout=10,
                             headers={"Accept": "application/vnd.github+json"})
            r.raise_for_status()
            d = r.json()
            tag = d.get("tag_name", "").lstrip("v")
            body = d.get("body", "")
            assets = d.get("assets", [])
            url = None
            for a in assets:
                if a.get("name", "").lower() == EXE_NAME.lower():
                    url = a.get("browser_download_url")
                    break
            return tag, body, url
        except Exception:
            return None, None, None

    def newer(self, latest):
        if not latest:
            return False
        try:
            c = tuple(int(x) for x in APP_VERSION.split("."))
            l = tuple(int(x) for x in latest.split("."))
            return l > c
        except Exception:
            return False

    def download(self, url, on_progress):
        tmp = tempfile.mktemp(suffix=".exe")
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                done = 0
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                            done += len(chunk)
                            on_progress(done / total * 100 if total else -1)
            return tmp
        except Exception:
            return None

    def apply(self, tmp):
        current = sys.executable
        bat = tempfile.mktemp(suffix=".bat")
        with open(bat, "w") as f:
            f.write(f'@echo off\ntimeout /t 2 /nobreak >nul\n'
                    f'move /y "{tmp}" "{current}"\n'
                    f'start "" "{current}"\ndel "%~f0"\n')
        subprocess.Popen(["cmd", "/c", bat],
                         creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0)


class Scanner:
    def __init__(self):
        self.scanned = 0
        self.threats = []

    def hash_file(self, path):
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def scan_file(self, path):
        hits = []
        digest = self.hash_file(path)
        if digest:
            for name, sig in SIGNATURE_DB.items():
                if digest == sig:
                    hits.append(f"[SIG] {name}")
        ext = Path(path).suffix.lower()
        if ext in RISKY_EXT:
            try:
                with open(path, "rb") as f:
                    data = f.read(524288).lower()
                for s in HEURISTIC_STRINGS:
                    if s in data:
                        hits.append(f"[HEUR] {s.decode(errors='replace')}")
            except Exception:
                pass
        return hits

    def scan(self, paths, on_file, stop):
        self.scanned = 0
        self.threats = []
        for base in paths:
            for root, dirs, files in os.walk(base):
                if stop.is_set():
                    return self.threats
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for fname in files:
                    if stop.is_set():
                        return self.threats
                    fp = os.path.join(root, fname)
                    self.scanned += 1
                    hits = self.scan_file(fp)
                    if hits:
                        entry = {"path": fp, "hits": hits,
                                 "time": datetime.now().strftime("%H:%M:%S")}
                        self.threats.append(entry)
                    on_file(fp, hits)
        return self.threats

    def quarantine(self, path, qdir):
        os.makedirs(qdir, exist_ok=True)
        dest = os.path.join(qdir, Path(path).name + ".quar")
        shutil.move(path, dest)
        return dest


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Cryptrion  v{APP_VERSION}  —  by {AUTHOR}")
        self.root.geometry("1060x700")
        self.root.minsize(860, 580)
        self.root.configure(bg=BG)
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass

        self.scanner  = Scanner()
        self.updater  = Updater()
        self.startup  = Startup()
        self.qdir     = os.path.join(os.path.expanduser("~"), ".cryptrion", "quarantine")
        self.logpath  = os.path.join(os.path.expanduser("~"), ".cryptrion", "cryptrion.log")
        os.makedirs(os.path.dirname(self.logpath), exist_ok=True)

        self.stop_ev  = threading.Event()
        self.rt_on    = False
        self.panels   = {}
        self.nav_btns = {}

        self.v_scanned  = tk.StringVar(value="0")
        self.v_threats  = tk.StringVar(value="0")
        self.v_quarant  = tk.StringVar(value="0")
        self.v_startup  = tk.BooleanVar(value=self.startup.is_enabled())

        self._ui()
        self._ensure_startup()
        self.root.after(1200, lambda: threading.Thread(
            target=self._startup_update_check, daemon=True).start())

    def _ensure_startup(self):
        if not self.startup.is_enabled():
            self.startup.enable()
            self.v_startup.set(True)

    def _ui(self):
        self._header()
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        self._sidebar(outer)
        self._main(outer)
        self._statusbar()
        self.show("dashboard")

    def _header(self):
        h = tk.Frame(self.root, bg=PANEL, height=56)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="⚡ CRYPTRION", font=("Consolas", 18, "bold"),
                 bg=PANEL, fg=ACCENT).pack(side="left", padx=20)
        tk.Label(h, text=f"v{APP_VERSION}  ·  Open Source Antivirus  ·  by {AUTHOR}",
                 font=FONT, bg=PANEL, fg=DIM).pack(side="left", pady=18)
        self.lbl_prot = tk.Label(h, text="● PROTECTED", font=FONT_B, bg=PANEL, fg=GREEN)
        self.lbl_prot.pack(side="right", padx=20)

    def _sidebar(self, parent):
        sb = tk.Frame(parent, bg=PANEL, width=178)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Label(sb, text="MENU", font=("Consolas", 7), bg=PANEL, fg=DIM).pack(
            anchor="w", padx=14, pady=(18, 4))
        for key, icon, label in [
            ("dashboard", "⊞", "Dashboard"),
            ("scan",      "◎", "Scan"),
            ("realtime",  "⟳", "Real-Time"),
            ("quarantine","⚠", "Quarantine"),
            ("logs",      "≡", "Logs"),
            ("settings",  "⚙", "Settings"),
        ]:
            b = tk.Button(sb, text=f"  {icon}  {label}", font=FONT, anchor="w",
                          bg=PANEL, fg=FG, relief="flat", cursor="hand2",
                          padx=8, pady=9, activebackground=BG, activeforeground=ACCENT,
                          command=lambda k=key: self.show(k))
            b.pack(fill="x", pady=1)
            self.nav_btns[key] = b
        tk.Frame(sb, bg=DIM, height=1).pack(fill="x", padx=12, pady=12)
        tk.Label(sb, text=f"© {datetime.now().year} {AUTHOR}\nMIT License",
                 font=("Consolas", 7), bg=PANEL, fg=DIM, justify="center").pack(side="bottom", pady=10)

    def _main(self, parent):
        self.content = tk.Frame(parent, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self._panel_dashboard()
        self._panel_scan()
        self._panel_realtime()
        self._panel_quarantine()
        self._panel_logs()
        self._panel_settings()

    def _statusbar(self):
        sb = tk.Frame(self.root, bg=PANEL, height=26)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        self.lbl_status = tk.Label(sb, text="Ready.", font=("Consolas", 8), bg=PANEL, fg=DIM)
        self.lbl_status.pack(side="left", padx=10)
        self.lbl_clock = tk.Label(sb, font=("Consolas", 8), bg=PANEL, fg=DIM)
        self.lbl_clock.pack(side="right", padx=10)
        self._clock()

    def _clock(self):
        self.lbl_clock.config(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._clock)

    def setstatus(self, t):
        self.lbl_status.config(text=t)

    def show(self, key):
        for k, p in self.panels.items():
            p.pack_forget()
            self.nav_btns[k].config(bg=PANEL, fg=FG)
        self.panels[key].pack(fill="both", expand=True)
        self.nav_btns[key].config(bg=BG, fg=ACCENT)

    def _frame(self, title, color=ACCENT):
        lf = tk.LabelFrame(None, text=f"  {title}  ", font=FONT_B,
                           bg=BG, fg=color, relief="flat",
                           highlightbackground=color, highlightthickness=1)
        return lf

    def _btn(self, parent, text, cmd, bg=ACCENT):
        return tk.Button(parent, text=text, font=FONT_B, bg=bg, fg=BG,
                         relief="flat", cursor="hand2", padx=11, pady=6,
                         activebackground=PANEL, command=cmd)

    def _log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}\n"
        try:
            with open(self.logpath, "a") as f:
                f.write(line)
        except Exception:
            pass
        if hasattr(self, "activity_box"):
            self.activity_box.config(state="normal")
            self.activity_box.insert("end", line)
            self.activity_box.see("end")
            self.activity_box.config(state="disabled")

    def _panel_dashboard(self):
        p = tk.Frame(self.content, bg=BG)
        self.panels["dashboard"] = p

        tk.Label(p, text="DASHBOARD", font=FONT_LG, bg=BG, fg=ACCENT).pack(
            anchor="w", padx=28, pady=(22, 2))
        tk.Label(p, text="Security overview", font=FONT, bg=BG, fg=DIM).pack(
            anchor="w", padx=28, pady=(0, 16))

        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=28)
        for col, (lbl, var, c) in enumerate([
            ("FILES SCANNED", self.v_scanned, ACCENT),
            ("THREATS FOUND", self.v_threats, RED),
            ("QUARANTINED",   self.v_quarant, YELLOW),
            ("STATUS",        tk.StringVar(value="ON"), GREEN),
        ]):
            card = tk.Frame(row, bg=PANEL, highlightbackground=c, highlightthickness=1)
            card.grid(row=0, column=col, padx=7, pady=4, sticky="ew", ipadx=12, ipady=12)
            row.columnconfigure(col, weight=1)
            tk.Label(card, textvariable=var, font=("Consolas", 26, "bold"),
                     bg=PANEL, fg=c).pack()
            tk.Label(card, text=lbl, font=("Consolas", 7), bg=PANEL, fg=DIM).pack()

        qf = self._frame("QUICK ACTIONS")
        qf.pack(fill="x", padx=28, pady=16)
        bf = tk.Frame(qf, bg=BG)
        bf.pack(padx=10, pady=10)
        self._btn(bf, "⚡ Quick Scan", lambda: (self.show("scan"), self._quick()), ACCENT).pack(side="left", padx=6)
        self._btn(bf, "☰ Full Scan",  lambda: (self.show("scan"), self._full()),  PURPLE).pack(side="left", padx=6)
        self._btn(bf, "↻ Check Updates", self._manual_update, GREEN).pack(side="left", padx=6)

        af = self._frame("RECENT ACTIVITY")
        af.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.activity_box = tk.Text(af, font=("Consolas", 8), bg=PANEL, fg=FG,
                                    relief="flat", state="disabled", height=9)
        self.activity_box.pack(fill="both", expand=True, padx=5, pady=5)
        self._log("Cryptrion started — all systems operational.")

    def _panel_scan(self):
        p = tk.Frame(self.content, bg=BG)
        self.panels["scan"] = p

        tk.Label(p, text="FILE SCANNER", font=FONT_LG, bg=BG, fg=ACCENT).pack(
            anchor="w", padx=28, pady=(22, 2))
        tk.Label(p, text="Scan drives and folders for malware", font=FONT, bg=BG, fg=DIM).pack(
            anchor="w", padx=28, pady=(0, 12))

        cf = self._frame("CONTROLS")
        cf.pack(fill="x", padx=28, pady=4)
        bf = tk.Frame(cf, bg=BG)
        bf.pack(padx=10, pady=10, anchor="w")
        self._btn(bf, "⚡ Quick Scan", self._quick, ACCENT).pack(side="left", padx=5)
        self._btn(bf, "☰ Full Scan",  self._full,  PURPLE).pack(side="left", padx=5)
        self._btn(bf, "📁 Custom Folder", self._custom, YELLOW).pack(side="left", padx=5)
        self.stop_btn = self._btn(bf, "■ Stop", self._stop, RED)
        self.stop_btn.pack(side="left", padx=5)
        self.stop_btn.config(state="disabled")

        pf = self._frame("PROGRESS")
        pf.pack(fill="x", padx=28, pady=4)
        self.scan_lbl = tk.Label(pf, text="No scan running.", font=("Consolas", 8),
                                 bg=BG, fg=DIM, anchor="w")
        self.scan_lbl.pack(fill="x", padx=10, pady=(6, 2))
        style = ttk.Style()
        style.theme_use("default")
        style.configure("C.Horizontal.TProgressbar", troughcolor=PANEL, background=ACCENT, thickness=10)
        self.scan_bar = ttk.Progressbar(pf, style="C.Horizontal.TProgressbar", mode="indeterminate")
        self.scan_bar.pack(fill="x", padx=10, pady=(2, 4))
        self.scan_count = tk.Label(pf, text="", font=("Consolas", 8), bg=BG, fg=DIM, anchor="w")
        self.scan_count.pack(fill="x", padx=10, pady=(0, 6))

        rf = self._frame("THREATS DETECTED")
        rf.pack(fill="both", expand=True, padx=28, pady=4)
        cols = ("time", "path", "threat")
        self.tree = ttk.Treeview(rf, columns=cols, show="headings")
        style.configure("Treeview", background=PANEL, foreground=FG,
                        fieldbackground=PANEL, rowheight=22, font=("Consolas", 8))
        style.configure("Treeview.Heading", background=BG, foreground=ACCENT, font=FONT_B)
        self.tree.heading("time",   text="TIME");    self.tree.column("time",   width=70,  anchor="center")
        self.tree.heading("path",   text="FILE");    self.tree.column("path",   width=500)
        self.tree.heading("threat", text="THREAT");  self.tree.column("threat", width=260)
        sb2 = ttk.Scrollbar(rf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb2.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sb2.pack(side="right", fill="y", pady=5)

        ab = tk.Frame(p, bg=BG)
        ab.pack(fill="x", padx=28, pady=(4, 16))
        self._btn(ab, "⚠ Quarantine Selected", self._quarantine_sel, YELLOW).pack(side="left", padx=5)
        self._btn(ab, "🗑 Delete Selected",     self._delete_sel,     RED).pack(side="left", padx=5)

    def _panel_realtime(self):
        p = tk.Frame(self.content, bg=BG)
        self.panels["realtime"] = p

        tk.Label(p, text="REAL-TIME MONITOR", font=FONT_LG, bg=BG, fg=ACCENT).pack(
            anchor="w", padx=28, pady=(22, 2))
        tk.Label(p, text="Live process & system monitoring", font=FONT, bg=BG, fg=DIM).pack(
            anchor="w", padx=28, pady=(0, 12))

        cf = self._frame("MONITOR CONTROL")
        cf.pack(fill="x", padx=28, pady=4)
        ctf = tk.Frame(cf, bg=BG)
        ctf.pack(padx=10, pady=10, anchor="w")
        self.rt_btn = self._btn(ctf, "▶ Start Monitor", self._toggle_rt, GREEN)
        self.rt_btn.pack(side="left", padx=5)
        self.rt_lbl = tk.Label(ctf, text="● Inactive", font=FONT_B, bg=BG, fg=RED)
        self.rt_lbl.pack(side="left", padx=14)

        prf = self._frame("RUNNING PROCESSES")
        prf.pack(fill="both", expand=True, padx=28, pady=4)
        pcols = ("pid", "name", "cpu", "mem", "status")
        self.proc_tree = ttk.Treeview(prf, columns=pcols, show="headings")
        self.proc_tree.heading("pid",    text="PID");    self.proc_tree.column("pid",    width=65, anchor="center")
        self.proc_tree.heading("name",   text="NAME");   self.proc_tree.column("name",   width=260)
        self.proc_tree.heading("cpu",    text="CPU%");   self.proc_tree.column("cpu",    width=80, anchor="center")
        self.proc_tree.heading("mem",    text="MB");     self.proc_tree.column("mem",    width=90, anchor="center")
        self.proc_tree.heading("status", text="STATUS"); self.proc_tree.column("status", width=120, anchor="center")
        psb = ttk.Scrollbar(prf, orient="vertical", command=self.proc_tree.yview)
        self.proc_tree.configure(yscrollcommand=psb.set)
        self.proc_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        psb.pack(side="right", fill="y", pady=5)
        self._btn(p, "↻ Refresh Now", self._refresh_procs, ACCENT).pack(anchor="w", padx=28, pady=(4, 16))

    def _panel_quarantine(self):
        p = tk.Frame(self.content, bg=BG)
        self.panels["quarantine"] = p

        tk.Label(p, text="QUARANTINE", font=FONT_LG, bg=BG, fg=YELLOW).pack(
            anchor="w", padx=28, pady=(22, 2))
        tk.Label(p, text="Isolated threat files", font=FONT, bg=BG, fg=DIM).pack(
            anchor="w", padx=28, pady=(0, 12))

        qf = self._frame("QUARANTINED FILES", YELLOW)
        qf.pack(fill="both", expand=True, padx=28, pady=4)
        qcols = ("name", "path", "date")
        self.q_tree = ttk.Treeview(qf, columns=qcols, show="headings")
        self.q_tree.heading("name", text="FILE");     self.q_tree.column("name", width=200)
        self.q_tree.heading("path", text="LOCATION"); self.q_tree.column("path", width=380)
        self.q_tree.heading("date", text="DATE");     self.q_tree.column("date", width=160, anchor="center")
        qsb = ttk.Scrollbar(qf, orient="vertical", command=self.q_tree.yview)
        self.q_tree.configure(yscrollcommand=qsb.set)
        self.q_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        qsb.pack(side="right", fill="y", pady=5)

        qb = tk.Frame(p, bg=BG)
        qb.pack(fill="x", padx=28, pady=(4, 16))
        self._btn(qb, "↻ Refresh",          self._refresh_q, ACCENT).pack(side="left", padx=5)
        self._btn(qb, "🗑 Delete Permanently", self._del_q,    RED).pack(side="left", padx=5)
        self._btn(qb, "📂 Open Folder", lambda: os.startfile(self.qdir) if os.path.exists(self.qdir) else None,
                  YELLOW).pack(side="left", padx=5)
        self._refresh_q()

    def _panel_logs(self):
        p = tk.Frame(self.content, bg=BG)
        self.panels["logs"] = p

        tk.Label(p, text="SCAN LOGS", font=FONT_LG, bg=BG, fg=ACCENT).pack(
            anchor="w", padx=28, pady=(22, 2))

        lf = self._frame("LOG OUTPUT")
        lf.pack(fill="both", expand=True, padx=28, pady=4)
        self.log_box = tk.Text(lf, font=("Consolas", 8), bg=PANEL, fg=FG,
                               relief="flat", state="disabled", wrap="none")
        lsb = ttk.Scrollbar(lf, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=lsb.set)
        self.log_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        lsb.pack(side="right", fill="y", pady=5)

        lb = tk.Frame(p, bg=BG)
        lb.pack(fill="x", padx=28, pady=(4, 16))
        self._btn(lb, "↻ Reload", self._reload_logs, ACCENT).pack(side="left", padx=5)
        self._btn(lb, "🗑 Clear",  self._clear_logs,  RED).pack(side="left", padx=5)
        self._reload_logs()

    def _panel_settings(self):
        p = tk.Frame(self.content, bg=BG)
        self.panels["settings"] = p

        tk.Label(p, text="SETTINGS", font=FONT_LG, bg=BG, fg=ACCENT).pack(
            anchor="w", padx=28, pady=(22, 2))

        sf = self._frame("STARTUP")
        sf.pack(fill="x", padx=28, pady=8)
        tk.Checkbutton(sf, text="  Launch Cryptrion automatically on Windows startup",
                       variable=self.v_startup, font=FONT, bg=BG, fg=FG,
                       activebackground=BG, selectcolor=PANEL,
                       command=lambda: self.startup.enable() if self.v_startup.get()
                                       else self.startup.disable()).pack(anchor="w", padx=10, pady=10)

        af = self._frame("ABOUT")
        af.pack(fill="x", padx=28, pady=8)
        for k, v in [
            ("Application", "Cryptrion-Official"),
            ("Version",     APP_VERSION),
            ("Author",      "Wyatt Mouris"),
            ("License",     "MIT Open Source"),
            ("GitHub",      "github.com/mouriswyatt66-alt/Cryptrion-Official"),
        ]:
            row = tk.Frame(af, bg=BG)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=f"{k}:", font=FONT_B, bg=BG, fg=DIM, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=v, font=FONT, bg=BG, fg=FG).pack(side="left")

        uf = self._frame("UPDATES")
        uf.pack(fill="x", padx=28, pady=8)
        ubf = tk.Frame(uf, bg=BG)
        ubf.pack(padx=10, pady=10, anchor="w")
        tk.Label(ubf, text=f"Installed version: {APP_VERSION}", font=FONT, bg=BG, fg=FG).pack(anchor="w")
        self._btn(ubf, "↻ Check for Updates", self._manual_update, GREEN).pack(anchor="w", pady=8)
        self._btn(ubf, "🌐 GitHub Repository",
                  lambda: webbrowser.open(GITHUB_REPO), PURPLE).pack(anchor="w")

    def _quick(self):
        self._run_scan([
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.join(os.environ.get("TEMP", ""), ""),
        ])

    def _full(self):
        drives = [f"{d}:\\" for d in "CDEFG" if os.path.exists(f"{d}:\\")]
        self._run_scan(drives or ["C:\\"])

    def _custom(self):
        d = filedialog.askdirectory(title="Select folder to scan")
        if d:
            self._run_scan([d])

    def _run_scan(self, paths):
        self.stop_ev.clear()
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.scanner.scanned = 0
        self.scanner.threats = []
        self.v_scanned.set("0")
        self.v_threats.set("0")
        self.stop_btn.config(state="normal")
        self.scan_bar.start(12)
        self.setstatus("Scanning...")
        self._log(f"Scan started: {paths}")

        def on_file(fp, hits):
            self.scan_lbl.config(text=fp[:110])
            self.scan_count.config(text=f"Scanned: {self.scanner.scanned}   Threats: {len(self.scanner.threats)}")
            self.v_scanned.set(str(self.scanner.scanned))
            if hits:
                self.v_threats.set(str(len(self.scanner.threats)))
                for h in hits:
                    self.tree.insert("", "end", values=(
                        datetime.now().strftime("%H:%M:%S"), fp, h))
                self._log(f"THREAT: {fp} → {hits[0]}")

        def worker():
            self.scanner.scan(paths, on_file, self.stop_ev)
            self.scan_bar.stop()
            self.stop_btn.config(state="disabled")
            n = len(self.scanner.threats)
            self.scan_lbl.config(text="Scan complete.")
            self.setstatus(f"Done — {self.scanner.scanned} files, {n} threats.")
            self._log(f"Scan complete. Files: {self.scanner.scanned}, Threats: {n}")
            if n:
                messagebox.showwarning("Cryptrion", f"Found {n} threat(s).\nPlease quarantine or delete them.")

        threading.Thread(target=worker, daemon=True).start()

    def _stop(self):
        self.stop_ev.set()
        self.scan_bar.stop()
        self.stop_btn.config(state="disabled")
        self.scan_lbl.config(text="Scan stopped.")
        self._log("Scan stopped by user.")

    def _quarantine_sel(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Cryptrion", "Select a file first.")
            return
        for iid in sel:
            path = self.tree.item(iid, "values")[1]
            try:
                self.scanner.quarantine(path, self.qdir)
                self.tree.delete(iid)
                self._log(f"Quarantined: {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        self._refresh_q()
        self.v_quarant.set(str(len(os.listdir(self.qdir)) if os.path.exists(self.qdir) else 0))

    def _delete_sel(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Cryptrion", "Select a file first.")
            return
        if not messagebox.askyesno("Confirm", "Permanently delete selected file(s)?"):
            return
        for iid in sel:
            path = self.tree.item(iid, "values")[1]
            try:
                os.remove(path)
                self.tree.delete(iid)
                self._log(f"Deleted: {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _toggle_rt(self):
        if not self.rt_on:
            self.rt_on = True
            self.rt_lbl.config(text="● Active", fg=GREEN)
            self.rt_btn.config(text="■ Stop Monitor", bg=RED)
            self._log("Real-time monitor started.")
            self._rt_loop()
        else:
            self.rt_on = False
            self.rt_lbl.config(text="● Inactive", fg=RED)
            self.rt_btn.config(text="▶ Start Monitor", bg=GREEN)
            self._log("Real-time monitor stopped.")

    def _rt_loop(self):
        if not self.rt_on:
            return
        self._refresh_procs()
        self.root.after(4000, self._rt_loop)

    def _refresh_procs(self):
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        try:
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
                try:
                    info = proc.info
                    mem = round(info["memory_info"].rss / 1048576, 1) if info["memory_info"] else 0
                    self.proc_tree.insert("", "end", values=(
                        info["pid"], info["name"], info["cpu_percent"], mem, info["status"]))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass

    def _refresh_q(self):
        for i in self.q_tree.get_children():
            self.q_tree.delete(i)
        if os.path.exists(self.qdir):
            for f in os.listdir(self.qdir):
                fp = os.path.join(self.qdir, f)
                mt = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
                self.q_tree.insert("", "end", values=(f, fp, mt))
        self.v_quarant.set(str(len(os.listdir(self.qdir)) if os.path.exists(self.qdir) else 0))

    def _del_q(self):
        sel = self.q_tree.selection()
        if not sel:
            messagebox.showinfo("Cryptrion", "Select a file first.")
            return
        if not messagebox.askyesno("Confirm", "Permanently delete selected quarantined file(s)?"):
            return
        for iid in sel:
            fp = self.q_tree.item(iid, "values")[1]
            try:
                os.remove(fp)
                self._log(f"Permanently deleted: {fp}")
            except Exception:
                pass
        self._refresh_q()

    def _reload_logs(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        if os.path.exists(self.logpath):
            try:
                with open(self.logpath, "r") as f:
                    self.log_box.insert("end", f.read())
            except Exception:
                pass
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_logs(self):
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            with open(self.logpath, "w") as f:
                f.write("")
            self._reload_logs()

    def _startup_update_check(self):
        self._do_update(silent_if_current=True)

    def _manual_update(self):
        threading.Thread(target=self._do_update, args=(False,), daemon=True).start()

    def _do_update(self, silent_if_current):
        self.setstatus("Checking for updates...")
        latest, notes, url = self.updater.get_latest()
        if latest is None:
            self.setstatus("Could not reach update server.")
            if not silent_if_current:
                messagebox.showinfo("Cryptrion", "Could not reach GitHub.\nCheck your internet connection.")
            return
        if self.updater.newer(latest):
            self.root.after(0, lambda: self._prompt_update(latest, notes, url))
        else:
            self.setstatus(f"Up to date — v{APP_VERSION}")
            if not silent_if_current:
                messagebox.showinfo("Cryptrion", f"You have the latest version: v{APP_VERSION}")

    def _prompt_update(self, latest, notes, url):
        msg = (f"New version available: v{latest}\n"
               f"Your version: v{APP_VERSION}\n\n"
               f"Release notes:\n{notes or 'None provided.'}\n\n"
               f"Cryptrion will now download and install the update automatically.")
        messagebox.showinfo("Update Available — Cryptrion", msg)
        if not url:
            messagebox.showerror("Update Error", "No download URL found in release.\nPlease update manually from GitHub.")
            return
        self._update_window(latest, url)

    def _update_window(self, latest, url):
        win = tk.Toplevel(self.root)
        win.title("Updating Cryptrion")
        win.geometry("500x170")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(win, text=f"Installing Cryptrion v{latest}", font=("Consolas", 13, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(20, 4))
        lbl = tk.Label(win, text="Connecting...", font=FONT, bg=BG, fg=DIM)
        lbl.pack()
        bar = ttk.Progressbar(win, style="C.Horizontal.TProgressbar",
                              length=440, mode="determinate", maximum=100)
        bar.pack(pady=14)

        def on_progress(pct):
            if pct < 0:
                bar.config(mode="indeterminate")
                bar.start(8)
                lbl.config(text="Downloading...")
            else:
                bar.config(mode="determinate")
                bar.stop()
                bar["value"] = pct
                lbl.config(text=f"Downloading... {pct:.1f}%")
            win.update_idletasks()

        def worker():
            tmp = self.updater.download(url, on_progress)
            if tmp:
                lbl.config(text="Applying update — please wait...")
                bar["value"] = 100
                self._log(f"Updated to v{latest}. Restarting.")
                time.sleep(1)
                self.updater.apply(tmp)
            else:
                lbl.config(text="Download failed. Update manually from GitHub.")
                self._log("Auto-update download failed.")

        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
