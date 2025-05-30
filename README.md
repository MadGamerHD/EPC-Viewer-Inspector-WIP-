## `.epc Texture Exporter` (Doctor Who Adventure Games)
This is a **very experimental** texture exporter for `.epc` files used in the **Doctor Who Adventure Games**. It allows you to scan `.epc` files for embedded textures, preview them, and export them in bulk.

> ⚠️ **Disclaimer:** This tool is highly experimental. Some files may not extract correctly, previews may fail, and functionality may vary between `.epc` files. Use at your own risk.
---

### 🔧 Features
* 📂 **Open .epc Files** – Load EPC game resource files.
* 🔍 **Analyze Textures** – Automatically scan for embedded texture names and offsets.
* 🖼️ **Preview Textures** – Preview selected textures within the app (supports standard formats).
* 💾 **Export All Textures** – Batch-export textures into a folder next to the EPC file.
* 📃 **Generate Report** – Save a scan report (`.txt`) listing found textures and their offsets.
---

### 🖥️ Usage

1. Run the script:
   ```bash
   python epc.py
   ```

2. Use the UI to:
   * **Open** an `.epc` file.
   * **Analyze** it to detect embedded texture references.
   * **Preview** a selected texture (some may fail).
   * **Export All** detected textures to a folder.

---

### 🧪 Known Limitations
* Not all embedded textures may be detected reliably.
* Some exported files may be corrupt or unreadable.
* Image preview may fail depending on the texture format or encoding.
* No official documentation exists for `.epc` files — this is based on reverse engineering.

---

### 📦 Dependencies
* [Python 3.x](https://www.python.org/)
* [Pillow (PIL)](https://python-pillow.org/)

Install Pillow with:

```bash
pip install pillow
```

---

### 🧠 Background
This tool was created for exploring textures in **Doctor Who Adventure Games**, which use `.epc` files to store game assets. Since the EPC format is undocumented, the logic is based on observed patterns and educated guesses.

---

### ✅ Credits
Made with love for Doctor Who fans and hobbyist modders.

---

### 📜 License
This project is released under the MIT License.
