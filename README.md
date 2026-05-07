# PassManager

> [Lire en français](README.fr.md)

A local, offline password manager built with Python and CustomTkinter. All data is encrypted and stored on your machine — nothing is sent to any server.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Master password** — single password to unlock the vault, derived with PBKDF2HMAC (SHA-256, 480 000 iterations)
- **AES encryption** — all credentials encrypted with Fernet (AES-128-CBC) before being written to disk
- **Local SQLite database** — stored in `%APPDATA%\PassManager\` on Windows, never in the app folder
- **Password generator** — configurable length, uppercase, lowercase, digits, symbols
- **Accent-insensitive search** — search `email` finds `émail`
- **One-click copy** — copy username or password to clipboard with a single click
- **Show / hide** — reveal individual passwords or all at once
- **Auto-logout** — automatic lock after 1 hour of inactivity
- **Encrypted export** — export the database as an encrypted `.db` backup file
- **CSV / TXT export** — export all entries to a plain-text CSV or TXT file (use with caution)
- **Font Awesome icons** — crisp vector icons, no rendering artifacts
- **Dark mode** — built-in dark theme

---

## Installation

### Option 1 — Installer or portable (recommended)

Download the latest version from the [Releases](../../releases) page:

- **`PassManager-x.x.x-Setup.exe`** — Classic installer (Start Menu shortcut, automatic uninstaller)
- **`PassManager-x.x.x-portable.zip`** — Portable version, extract and run `PassManager.exe`, no installation required

### Option 2 — Run from source

**Requirements:** Python 3.11+

```bash
git clone https://github.com/your-username/PassManager.git
cd PassManager
pip install -r requirements.txt
python PassManager.py
```

---

## Build

The executable is built automatically via GitHub Actions on every `v*` tag push.

To build locally:

```bash
pip install -r requirements.txt
pyinstaller PassManager.spec
# Output: dist/PassManager.exe
```

---

## Security

| Layer | Detail |
|---|---|
| Key derivation | PBKDF2HMAC · SHA-256 · 480 000 iterations |
| Encryption | Fernet (AES-128-CBC + HMAC-SHA256) |
| Storage | Local SQLite · `%APPDATA%\PassManager\` |
| Memory | Master password never stored in plain text |
| Auto-lock | Session locks after 1 hour of inactivity |

> **The database file is excluded from the repository** (see `.gitignore`). Never commit `passwords.db`.

---

## Project structure

```
PassManager/
├── PassManager.py          # Main application
├── PassManager.spec        # PyInstaller build config
├── requirements.txt        # Python dependencies
├── passmanager_icon.ico    # Application icon
├── fa-solid-900.ttf        # Font Awesome (icons)
└── .github/
    └── workflows/
        └── build-release.yml
```

---

## Release

Push a version tag to trigger an automated build and GitHub Release:

```bash
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

---

## Author

Developed by edurel with [Claude AI](https://claude.ai) (Anthropic).

---

## License

MIT
