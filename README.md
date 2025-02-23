# FRIDAY - Your Personal AI Assistant 🤖

**FRIDAY** is an AI-powered personal assistant capable of understanding voice and text commands, executing system functions, fetching web data, and assisting in various tasks such as playing music, taking screenshots, and even creating project structures.

## 🚀 Features

- 🎤 **Voice Recognition & Text Input**: Accepts commands through both voice and text.
- 🔊 **Text-to-Speech (TTS)**: Provides audio feedback using `pyttsx3`.
- 🧠 **NLP-Powered Command Processing**: Uses `Spacy` and fuzzy matching to understand commands.
- 📚 **Customizable Learning Mode**: Stores past user interactions to improve response accuracy.
- 🖥️ **System Control**: Can adjust volume, take screenshots, open camera, and perform system shutdowns.
- 🌍 **Web Search & Automation**: Fetches Google summaries, plays music from YouTube, and opens web pages.
- 🏗️ **Project Structure Generator**: Helps create structured project directories for different development categories.

## 🔧 Installation

### Prerequisites

Ensure you have the following installed on your system:

- 🐍 Python 3.x
- 📦 Required Python libraries:
  ```sh
  pip install pyttsx3 SpeechRecognition opencv-python pyautogui pywhatkit fuzzywuzzy beautifulsoup4 requests spacy
  ```
- 📥 Download the English NLP model for Spacy:
  ```sh
  python -m spacy download en_core_web_sm
  ```

## ▶️ How to Run

1. Run the script:
   ```sh
   python FRIDAY.py
   ```
2. FRIDAY will greet you and ask if you want to enable learning mode.
3. Say or type **"Wake up"** to activate FRIDAY.
4. Give commands such as:
   - 🕒 "What is the time?"
   - 🔍 "Open Google"
   - 📸 "Take a screenshot"
   - 🏗️ "Create project"
5. Say **"Go to sleep"** to deactivate FRIDAY until needed again.

## 🗂️ Available Commands

- ⏰ **"Time"**, 📅 **"Date"**, 📆 **"Day"** - Fetches the current time, date, or day.
- 🎵 **"Play music"** - Plays a song on YouTube.
- 🔍 **"Open Google"** - Opens a Google search with a spoken query.
- 📸 **"Take screenshot"** - Captures and saves a screenshot.
- 🎥 **"Open camera"** - Opens the system camera.
- 🔊 **"Increase volume"**, 🔉 **"Decrease volume"** - Adjusts system volume.
- 🏗️ **"Create project"** - Assists in creating structured project directories.
- 💻 **"Shutdown laptop"**, 🔄 **"Restart laptop"**, 🔒 **"Lock laptop"** - System control commands.
- 🚀 **And many more!**

## 🧠 Learning Mode

FRIDAY can store past interactions to improve command recognition. Enable or disable this feature at startup.

## ⚙️ Customization

- Modify or add commands in the `commands` dictionary in `FRIDAY.py`.
- Adjust TTS settings (voice and rate) in `engine.setProperty()`.

## 📜 License

This project is open-source and free to use. Modify and distribute as needed!

---

Developed with ❤️ by MANVIT M DESHMUKH


