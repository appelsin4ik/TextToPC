# 🚀 TextBridge

> Write on your phone — get it instantly on your PC.

TextBridge is a lightweight cross-device utility that allows you to send text from your Android phone directly to your Windows computer over a local network.

Perfect for quickly transferring:
- 🔗 Links
- 📝 Notes
- 💻 Commands
- 🧠 Ideas
- 📦 Code snippets

## ✨ Features

- ⚡ Instant text transfer over Wi-Fi
- 📋 Automatic clipboard copy on PC
- 🖥️ Modern desktop UI (CustomTkinter)
- 📱 Clean Android interface
- 💾 Optional message history (JSON)
- 🧠 Persistent settings via Windows Registry
- 📌 Always-on-top window toggle
- 🎨 Smooth animated message bubbles
- 🧩 Simple and minimal setup

## 🧱 Project Structure

```bash
TextBridge/
├─ desktop/ # Windows desktop app
├─ android/ # Android app (Android Studio project)
├─ README.md
└─ .gitignore
```

## ⚙️ How It Works

1. The desktop app runs a local server on your PC
2. The Android app sends text via Wi-Fi (HTTP)
3. The PC receives it instantly
4. Text is automatically copied to clipboard
5. Messages appear in a styled UI

## 🚀 Quick Start

### 🖥️ Desktop

```bash
cd desktop
pip install -r requirements.txt
python server_gui.py
```

---

### 📱 Android

1. Open the android/ folder in Android Studio
2. Build APK or run on device
3. Make sure both devices are on the same Wi-Fi
4. Send text — done

---

### 📦 Releases

Prebuilt versions are available in the Releases section:

- 🪟 Windows `.exe`
- 📱 Android `.apk`

---

### 🎯 Use Cases

- Send links from phone → PC instantly
- Copy commands without typing
- Share notes between devices
- Use phone as wireless text input

---

### 🛣️ Roadmap

- 📤 Share intent (send directly from apps)
- 🧩 File & image transfer
- 🔍 Message search
- 🔔 Notifications
- 🧊 Compact mode
- 📡 QR connection setup

--- 

### 🧠 Philosophy

TextBridge is built as a simple, fast, no-friction tool
— no accounts, no cloud, no complexity.

Just your devices. Just your network.

---

### 📄 License

Personal project — free to use and modify.

---

### ⛓️ Links

[> Text Bridge - Desktop Setup](desktop/README.md) <p>
[> Text Bridge - Android Setup](android/README.md)
