# YOTO JSON Extractor

**YOTO JSON Extractor** is a Python-based tool that helps you download and process JSON data from Yoto URLs. It extracts audio files and images, organizes them into folders, and embeds metadata into audio files for easier management of Yoto card content.

---

## Features

- **Extracts JSON**: Downloads and processes JSON from multiple Yoto URLs at once.
- **Audio and Image Downloading**: Downloads audio files (AAC/MP3) and their associated images.
- **Metadata Embedding**: Automatically embeds metadata such as title, album, artist, genre, and year into audio files.
- **Automated Folder Management**: Organizes downloaded files into respective folders for audio and images.
- **Automatic Cleanup**: Deletes the JSON file after the extraction process.

---

## Installation

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

### Dependencies

This project requires the following Python libraries:

- **requests** – For handling HTTP requests to download JSON and media.
- **beautifulsoup4** – To parse HTML and extract relevant data.
- **mutagen** – For embedding metadata into audio files (supports AAC and MP3).
- **customtkinter** – For creating a modern graphical user interface (GUI).

---

## Usage

1. Run the script using Python:

   ```bash
   python YOTO.py
   ```

2. Enter the Yoto URLs (one per line) into the provided text area.
3. Click the "Extract files" button to begin the extraction process.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
