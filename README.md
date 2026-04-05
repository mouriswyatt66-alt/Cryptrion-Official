<div align="center">

```
 ██████╗██████╗ ██╗   ██╗██████╗ ████████╗██████╗ ██╗ ██████╗ ███╗   ██╗
██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗██║██╔═══██╗████╗  ██║
██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██████╔╝██║██║   ██║██╔██╗ ██║
██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══██╗██║██║   ██║██║╚██╗██║
╚██████╗██║  ██║   ██║   ██║        ██║   ██║  ██║██║╚██████╔╝██║ ╚████║
 ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

# Cryptrion-Official

**Free open-source Windows antivirus — by Wyatt Mouris**

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-yellow.svg)]()
[![GitHub Release](https://img.shields.io/github/v/release/mouriswyatt66-alt/Cryptrion-Official)](https://github.com/mouriswyatt66-alt/Cryptrion-Official/releases/latest)
[![Author](https://img.shields.io/badge/Made%20by-Wyatt%20Mouris-purple.svg)]()

</div>

---

## What is Cryptrion?

Cryptrion is a **free, open-source antivirus** for Windows created by **Wyatt Mouris**.  
It uses SHA-256 signature matching and heuristic string analysis to find malware, monitors your running processes live, safely quarantines threats, and **auto-updates itself directly from GitHub Releases** — no manual updates needed.

---

## Features

| Feature | Description |
|---|---|
| ⚡ Quick Scan | Scans Downloads, Desktop, and Temp instantly |
| ☰ Full System Scan | Scans every drive on your PC |
| 📁 Custom Scan | Choose any folder |
| 🔎 Signature Detection | SHA-256 matching against known malware hashes |
| 🧠 Heuristic Analysis | Detects suspicious patterns inside files |
| ⟳ Real-Time Monitor | Watches all running processes live |
| ⚠ Quarantine | Safely isolates threats |
| 🔄 Auto-Update | Checks GitHub on every launch, force-installs updates with a live progress bar |
| 🚀 Startup | Adds itself to Windows startup automatically |
| 📋 Logs | Full persistent log of every scan and threat |

---

## Download

👉 [**Download Cryptrion.exe from Releases**](https://github.com/mouriswyatt66-alt/Cryptrion-Official/releases/latest)

No install needed. Just right-click → **Run as Administrator**.

---

## How the Auto-Update Works

Every time Cryptrion launches it calls:
```
GET https://api.github.com/repos/mouriswyatt66-alt/Cryptrion-Official/releases/latest
```
If the release tag is newer than the running version, Cryptrion:
1. Shows an update prompt (cannot be skipped)
2. Downloads the new `Cryptrion.exe` from the release assets
3. Shows a **live download progress bar**
4. Applies the update and restarts automatically

---

## Build from Source

### Requirements
- Windows 10 or 11
- Python 3.11+
- Visual Studio Code (recommended)

### Steps

```bash
# 1. Clone
git clone https://github.com/mouriswyatt66-alt/Cryptrion-Official.git
cd Cryptrion-Official

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run from source (for development)
python cryptrion.py

# 4. Build the EXE
BUILD.bat
```

The finished EXE will be at **`dist\Cryptrion.exe`**.

---

## How to Publish a New Release

1. Edit `APP_VERSION` in `cryptrion.py` — e.g. change `"1.0.0"` to `"1.1.0"`
2. Commit and push
3. Create a GitHub Release tagged `v1.1.0`
4. Upload `dist\Cryptrion.exe` as a release asset named exactly `Cryptrion.exe`
5. Every running copy of Cryptrion will detect and force-install the update automatically

---

## Project Layout

```
Cryptrion-Official/
├── cryptrion.py       ← Full application source
├── Cryptrion.spec     ← PyInstaller build config
├── BUILD.bat          ← One-click build script
├── requirements.txt   ← Python dependencies
├── LICENSE            ← MIT License
└── README.md          ← This file
```

---

## Contributing

Cryptrion is fully open source. PRs welcome!

1. Fork the repo
2. Create a branch: `git checkout -b my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push and open a Pull Request

---

## Disclaimer

Cryptrion is an independent open-source project provided as-is under the MIT license.  
It is not affiliated with any commercial security vendor. Use alongside other security practices for best protection.

---

## License

[MIT License](LICENSE) — Copyright © 2024 **Wyatt Mouris**

---

<div align="center">
Built with ⚡ by <strong>Wyatt Mouris</strong>
</div>
