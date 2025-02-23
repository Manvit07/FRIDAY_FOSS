import customtkinter as ctk
import threading
import pyttsx3
import speech_recognition as sr
import datetime
import os
import cv2
import pyautogui
import time
import pywhatkit as wk
from difflib import get_close_matches
import spacy
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import requests
import webbrowser
import random
import json
import queue
from PIL import Image

class FridayGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize basic attributes first
        self.is_listening = False
        self.use_voice = True
        self.learning_mode = False
        
        # Configure window
        self.title("F.R.I.D.A.Y")
        self.geometry("800x600")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create message queue for thread-safe communication
        self.message_queue = queue.Queue()
        
        # Initialize FRIDAY components
        self.initialize_friday_components()
        
        # Create widgets
        self.create_widgets()
        
        # Start queue processing
        self.process_queue()
        
        # Start voice recognition if enabled
        if self.use_voice:
            self.start_voice_recognition()

    def toggle_voice_mode(self):
        """Toggle between voice and text input modes"""
        self.use_voice = not self.use_voice
        self.voice_button.configure(text="Voice: ON" if self.use_voice else "Voice: OFF")
        mode = "voice mode" if self.use_voice else "text mode"
        self.speak_and_display(f"Switched to {mode}")
        
        if self.use_voice:
            self.start_voice_recognition()

    def toggle_wake_sleep(self):
        """Toggle between wake and sleep states"""
        if self.is_listening:
            self.is_listening = False
            self.wake_button.configure(text="Wake FRIDAY")
            self.speak_and_display("Going to sleep. Click 'Wake FRIDAY' when you need me.")
        else:
            self.is_listening = True
            self.wake_button.configure(text="Sleep FRIDAY")
            self.speak_and_display("FRIDAY in your service. How can I help you today?")
            if self.use_voice:
                self.start_voice_recognition()

    def start_voice_recognition(self):
        """Start continuous voice recognition in a separate thread"""
        if not hasattr(self, 'voice_thread') or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=self.voice_recognition_loop)
            self.voice_thread.daemon = True
            self.voice_thread.start()

    def voice_recognition_loop(self):
        """Continuous voice recognition loop"""
        r = sr.Recognizer()
        while True:
            if not self.is_listening or not self.use_voice:
                time.sleep(0.1)
                continue
                
            with sr.Microphone() as source:
                try:
                    self.status_label.configure(text="Status: Listening...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=1, phrase_time_limit=5)
                    self.status_label.configure(text="Status: Processing...")
                    
                    query = r.recognize_google(audio, language='en-in')
                    self.status_label.configure(text="Status: Ready")
                    self.update_output(f"You said: {query}", "user")
                    self.process_command(query.lower())
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    self.update_output("Could not request results. Check your internet connection.", "system")
                except Exception as e:
                    print(f"Error in voice recognition: {e}")
                    continue

    def get_song_name(self):
        """Get song name through voice recognition"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_output("Listening for song name...", "system")
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source)
                song = r.recognize_google(audio, language='en-in')
                self.update_output(f"Playing: {song}", "assistant")
                wk.playonyt(song)
            except sr.UnknownValueError:
                self.update_output("Sorry, I did not catch the song name.", "system")

    def open_camera(self):
        """Open and handle camera operations"""
        threading.Thread(target=self.camera_thread).start()

    def camera_thread(self):
        """Handle camera operations in a separate thread"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.speak_and_display("Error: Could not open camera.")
            return
            
        self.update_output("Camera opened. Press 'q' to quit.", "system")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                self.speak_and_display("Error: Failed to capture frame.")
                break
                
            cv2.imshow("FRIDAY Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

    def take_screenshot(self):
        """Handle screenshot functionality"""
        self.speak_and_display("Tell me a name for the file")
        if self.use_voice:
            threading.Thread(target=self.get_screenshot_name).start()
        else:
            self.input_entry.configure(placeholder_text="Enter screenshot name...")

    def get_screenshot_name(self):
        """Get screenshot name through voice recognition"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_output("Listening for file name...", "system")
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source)
                name = r.recognize_google(audio, language='en-in')
                self.save_screenshot(name)
            except sr.UnknownValueError:
                self.update_output("Sorry, I did not catch the file name.", "system")

    def save_screenshot(self, name):
        """Save the screenshot with the given name"""
        screenshot_directory = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        if not os.path.exists(screenshot_directory):
            os.makedirs(screenshot_directory)
        
        file_path = os.path.join(screenshot_directory, f"{name}.png")
        time.sleep(2)  # Give time to prepare
        img = pyautogui.screenshot()
        img.save(file_path)
        self.speak_and_display(f"Screenshot saved as {file_path}")

    def ok_google(self):
        """Handle Google search functionality"""
        self.speak_and_display("What should I search for you?")
        if self.use_voice:
            threading.Thread(target=self.get_search_query).start()
        else:
            self.input_entry.configure(placeholder_text="Enter search query...")

    def get_search_query(self):
        """Get search query through voice recognition"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_output("Listening for search query...", "system")
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source)
                query = r.recognize_google(audio, language='en-in')
                self.perform_search(query)
            except sr.UnknownValueError:
                self.update_output("Sorry, I did not catch the search query.", "system")

    def perform_search(self, query):
        """Perform Google search and get summary"""
        try:
            summary = self.get_google_summary(query)
            self.speak_and_display(summary)
            webbrowser.open(f"https://www.google.com/search?q={query}")
            self.speak_and_display("These are some of the most viewed sites.")
        except Exception as e:
            self.speak_and_display("Sorry, I encountered an error while searching.")

    def get_google_summary(self, query):
        """Get summary from Google search results"""
        search_url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        summary = soup.find('div', {'class': 'BNeawe s3v9rd AP7Wnd'})
        return summary.text if summary else "I could not find a summary for that topic."

    def initialize_friday_components(self):
        """Initialize all FRIDAY components including TTS and NLP"""
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 200)
        
        # Initialize NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.update_output("Installing required NLP model...", "system")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load project structures
        self.load_project_structures()
        
        # Initialize commands dictionary
        self.initialize_commands()

    def initialize_commands(self):
        """Initialize the commands dictionary with all available commands"""
        self.commands = {
            "switch mode": self.toggle_voice_mode,
            "time": lambda: self.speak_and_display(f"The time is {self.get_time()}"),
            "date": lambda: self.speak_and_display(f"Today's date is {self.get_date()}"),
            "day": lambda: self.speak_and_display(f"Today is {self.get_day()}"),
            "create project": self.create_project,
            "play music": self.open_youtube,
            "open camera": self.open_camera,
            "take screenshot": self.take_screenshot,
            "increase volume": self.volume_up,
            "decrease volume": self.volume_down,
            "open google": self.ok_google,
            "shutdown laptop": lambda: os.system("shutdown /s /t 5"),
            "restart laptop": lambda: os.system("shutdown /r /t 5"),
            "lock laptop": lambda: os.system("rundll32.exe user32.dll,LockWorkStation"),
        }

    def create_project(self):
        """Handles user input to create a project directory structure."""
        self.speak_and_display("Which type of project structure do you need?")
        categories = ["frontend", "backend", "data science", "machine learning", "mobile app", "cpp project", "c project"]
        self.speak_and_display("Available categories: " + ", ".join(categories))
        if self.use_voice:
            threading.Thread(target=self.get_project_category).start()
        else:
            self.input_entry.configure(placeholder_text="Enter project category...")
    
    def create_project_structure(self, category):
        """Create the project structure based on the selected category"""
        if category in self.project_structures:
            structure_details = random.choice(self.project_structures[category])["details"]
            self.speak_and_display("Creating project structure...")
            self.create_project_structure_from_text("my_project", structure_details)
            self.speak_and_display("Project has been successfully created.")
        else:
            self.speak_and_display("Invalid category. Please try again.")

    def get_project_category(self):
        """Get project category through voice recognition"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_output("Listening for project category...", "system")
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source)
                category = r.recognize_google(audio, language='en-in').lower()
                self.create_project_structure(category)
            except sr.UnknownValueError:
                self.update_output("Sorry, I did not catch the category.", "system")

    def load_project_structures(self):
        """Loads predefined project structures"""
        try:
            with open("project_structures.json", "r", encoding="utf-8") as f:
                self.project_structures = json.load(f)
        except FileNotFoundError:
            self.project_structures = {}
            self.update_output("Project structures file not found.", "system")

    def create_widgets(self):
        """Create UI widgets for the application"""
        
        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", font=("Arial", 14))
        self.status_label.pack(pady=5)
        
        # Input field for user commands
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=20, pady=5)
        
        self.input_entry = ctk.CTkEntry(self.input_frame, width=500, placeholder_text="Enter your command...")
        self.input_entry.pack(side="left", padx=5)
        self.input_entry.bind("<Return>", lambda event: self.send_command())

        # Execute Button
        self.execute_button = ctk.CTkButton(self.input_frame, text="Execute", command=self.send_command)
        self.execute_button.pack(side="left", padx=5)

        # Voice Command Toggle Button
        self.voice_button = ctk.CTkButton(
            self.input_frame, 
            text="Voice: ON" if self.use_voice else "Voice: OFF",
            command=self.toggle_voice_mode
        )
        self.voice_button.pack(side="left", padx=5)

        # Output text area with scrollbar
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.output_text = ctk.CTkTextbox(self.output_frame, width=700, height=400)
        self.output_text.pack(fill="both", expand=True)
        
        # Wake/Sleep button
        self.wake_button = ctk.CTkButton(
            self,
            text="Wake FRIDAY",
            command=self.toggle_wake_sleep
        )
        self.wake_button.pack(pady=10)

    def process_queue(self):
        """Process messages from the queue"""
        try:
            while not self.message_queue.empty():
                message, message_type = self.message_queue.get_nowait()
                self.output_text.insert("end", message + "\n")
                self.output_text.see("end")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def update_output(self, message, message_type="info"):
        """Add message to output text area with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        
        if message_type == "user":
            prefix = "You"
        elif message_type == "assistant":
            prefix = "FRIDAY"
        else:
            prefix = "System"
            
        formatted_message = f"[{timestamp}] {prefix}: {message}"
        self.message_queue.put((formatted_message, message_type))

    def speak_and_display(self, message):
        """Speak the message and display it in the output area"""
        self.update_output(message, "assistant")
        threading.Thread(target=self.speak, args=(message,)).start()

    def speak(self, audio):
        """Speak the given audio text"""
        self.engine.say(audio)
        self.engine.runAndWait()

    def send_command(self):
        """Handle sending commands (both voice and text)"""
        command = self.input_entry.get().lower()
        if command:
            self.update_output(command, "user")
            self.input_entry.delete(0, "end")
            self.process_command(command)

    def process_command(self, query):
        """Process the received command"""
        if query in self.commands:
            self.commands[query]()
        else:
            matched_command = self.match_command(query)
            if matched_command:
                self.update_output(f"Executing: {matched_command}", "assistant")
                self.commands[matched_command]()
            else:
                self.speak_and_display("Sorry, I didn't understand that command.")

    def match_command(self, user_query):
        """Matches user query with available commands using fuzzy matching"""
        command_list = list(self.commands.keys())
        best_match, score = process.extractOne(user_query, command_list)
        return best_match if score > 60 else None

    # Core functionality methods
    def get_time(self):
        return datetime.datetime.now().strftime("%H:%M")
    
    def get_date(self):
        return datetime.datetime.now().strftime('%d %B %Y')
    
    def get_day(self):
        return datetime.datetime.now().strftime("%A")

    def open_youtube(self):
        self.speak_and_display("Which song would you like to listen to?")
        if self.use_voice:
            threading.Thread(target=self.get_song_name).start()
        else:
            self.input_entry.configure(placeholder_text="Enter song name...")

    def volume_up(self):
        for _ in range(5):
            pyautogui.press("volumeup")
        self.speak_and_display("Volume increased")
    
    def volume_down(self):
        for _ in range(5):
            pyautogui.press("volumedown")
        self.speak_and_display("Volume decreased")
    
    def ok_google(self):
        self.speak_and_display("What should I search for you?")
        if self.use_voice:
            threading.Thread(target=self.get_search_query).start()
        else:
            self.input_entry.configure(placeholder_text="Enter search query...")
    
    def get_search_query(self):
        """Get search query through voice recognition"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_output("Listening for search query...", "system")
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source)
                query = r.recognize_google(audio, language='en-in')
                self.perform_search(query)
            except sr.UnknownValueError:
                self.update_output("Sorry, I did not catch the search query.", "system")
    
    def perform_search(self, query):
        """Perform Google search and get summary"""
        summary = self.get_google_summary(query)
        self.speak_and_display(summary)
        webbrowser.open(f"https://www.google.com/search?q={query}")
        self.speak_and_display("These are some of the most viewed sites.")
    
    def get_google_summary(self, query):
        """Get summary from Google search results"""
        search_url = f"https://www.google.com/search?q={query}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        summary = soup.find('span', {'class': 'aCOpRe'})
        return summary.text if summary else "I could not find a summary for that topic."
    
    # Learning Mode Functions
    def store_interaction(self, user_input, system_response):
        """Stores user commands and system responses for learning"""
        data = self.load_past_interactions()
        data[user_input] = system_response
        
        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)
    
    def load_past_interactions(self):
        """Loads stored user interactions from file"""
        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                return json.load(file)
        return {}
    
    def load_project_structures(self):
        """Loads predefined project structures"""
        try:
            with open("project_structures.json", "r", encoding="utf-8") as f:
                self.project_structures = json.load(f)
        except FileNotFoundError:
            self.project_structures = {}
            self.update_output("Project structures file not found.", "system")

if __name__ == "__main__":
    app = FridayGUI()
    app.mainloop()