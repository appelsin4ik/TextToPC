# 🖥️ TextBridge Desktop

> Receive text from your Android phone instantly on your Windows PC.

## ✨ Features

- 📥 Receives text over local network
- 📋 Automatically copies to clipboard
- 🧠 Optional persistent history (`history.json`)
- 🔁 Toggle history ON/OFF
- 🪟 Always-on-top window
- 🎨 Modern dark UI with animations
- 🔍 Select and copy text manually
- 📊 Message stats (count + size)

## ⚙️ Requirements

- Windows
- Python 3.10+
- Same Wi-Fi network as Android device

## Dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install flask pyperclip customtkinter
```

---

### 🚀 Run

```bash
python server_gui.py #from /desktop
```

Run without console:

```bash
pythonw server_gui.py
```

---

### 📦 Build EXE

```bash
python -m PyInstaller --clean --onefile --windowed --icon=text.ico --add-data "text.ico;." --name TextBridge server_gui.py
```
---

### 🧠 History System

When enabled:

- messages saved in `history.json`
- restored on next launch

When disabled:

- file is deleted
- state stored in `Windows Registry`

---

### 📁 Files

- `server_gui.py` — main application
- `text.ico` — app icon
- `requirements.txt` — dependencies

---

### 🛠️ Tips

- Make sure port 5000 is open
- PC and phone must be on same network
- If connection fails → check firewall

