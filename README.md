# 🎵🎶 **YOTO JSON Extractor** 🎶🎵

![Code Size](https://img.shields.io/github/languages/code-size/afsenovilla/YOTO-json-extractor) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**YOTO JSON Extractor** is a Python-based tool that helps you download and process JSON data from Yoto URLs. It extracts and compress audio files and images, and embeds metadata into audio files for easier management of Yoto card content.

---

## ✨ Features

- **Extracts JSON**: Downloads and processes information from multiple Yoto URLs at once.
- **Audio and Image Downloading**: Downloads audio files (AAC/MP3) and their associated images.
- **Metadata Embedding**: Automatically embeds metadata such as title, track, album, artist and genre into audio files.
- **Automated Management**: Organizes downloaded cards into respective compressed folders with audio and images.
- **Automatic Cleanup**: Deletes the folders and JSON files after the extraction process.

---

## 💾 Compiled Version

### **Executable File Available!**
A **compiled version** of the YOTO JSON Extractor is available as an executable file (`.exe`). 

#### **Benefits of the Executable Version:**
- **No Installation Required:** Users can run the application without needing to install Python or any dependencies.
- **User-Friendly:** Simply double-click the executable file to start using the tool, making it accessible for all users.

To get started with the executable version, just download the `.exe` file from the Releases section and double-click to run!

---

## ⚙️ Installation 

### 1. Clone the Repository

Clone this repository to your local machine using the following command:

```bash
git clone https://github.com/afsenovilla/YOTO-json-extractor.git
cd YOTO-json-extractor
```

### 2. Install Dependencies

Make sure you have Python installed. Then install the required Python packages by running:

```bash
pip install -r requirements.txt
```

#### 📦 Dependencies

This project requires the following Python libraries:

- **requests**: For handling HTTP requests to download JSON and media.
- **beautifulsoup4**: To parse HTML and extract relevant data.
- **mutagen**: For embedding metadata into audio files (supports AAC and MP3).
- **customtkinter**: For creating a modern graphical user interface (GUI).
- **py7zr**: For handling compressed files in `.7z` format.

---

## 🛠️ Usage 

1. Run the script using Python:

   ```bash
   python YOTO.py
   ```

2. Input one or multiple YOTO URLs into the text area.
3. Click the "Extract files" button to start the download and processing.
4. The processed files and folders will be saved and the compressed in the directory of your choice.

---

## 📋 Fequently Asked Questions 

### 1. How do I get the URL from a YOTO card?
To extract the URL from a physical YOTO card, you'll need a smartphone and the **NXP TagInfo** app, available for both iOS and Android.

**Steps:**
1. Download and install the **NXP TagInfo** app from the [App Store](https://apps.apple.com/es/app/nfc-taginfo-by-nxp/id1246143596) or [Google Play Store](https://play.google.com/store/apps/details?id=com.nxp.taginfolite).
2. Open the app and touch the **Scan & Launch** button.
2. Tap the YOTO card against the NFC reader on your smartphone.
3. The app will read the NFC tag and display the URL associated with the YOTO card.
4. Copy the URL and paste it in the **YOTO JSON Extractor**.

### 2. What should I do if the download fails?
Ensure that the provided YOTO URL is correct. If the issue persists, check your internet connection.

### 3. Can I process multiple URLs at once?
Yes! You can input multiple YOTO URLs separated by new lines in the **YOTO JSON Extractor** and process them in batches.

### 4. What file formats are supported?
The tool currently supports downloading audio files in **AAC** or **MP3** format, depending on what’s available in the YOTO JSON data.

---

## 📝 To-Do List

- [X] Add progress bar to the GUI for download status
- [X] Add user settings for customizing download options
- [ ] Improve metadata customization options
- [X] Implement support for more audio formats
- [ ] Optimize error handling for specific network issues
- [ ] Test cross-platform compatibility
- [ ] Make the app available for macOS users
- [ ] Make the app available for Linux users
- [X] Create a logo


---

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
